from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from . import models, schemas
from .security import hash_password


def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    # Создание пользователя с проверкой уникальности логина.
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(status_code=409, detail="Username already exists")
    user = models.User(
        username=user_in.username,
        full_name=user_in.full_name,
        role=user_in.role,
        password_hash=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: models.User, user_in: schemas.UserUpdate) -> models.User:
    changes = user_in.model_dump(exclude_unset=True)
    if "password" in changes:
        user.password_hash = hash_password(changes.pop("password"))
    for field, value in changes.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def create_product(db: Session, product_in: schemas.ProductCreate) -> models.Product:
    # SKU выступает бизнес-идентификатором товара и не должен повторяться.
    if db.query(models.Product).filter(models.Product.sku == product_in.sku).first():
        raise HTTPException(status_code=409, detail="SKU already exists")
    product = models.Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def apply_movement(db: Session, movement_in: schemas.MovementCreate) -> models.StockMovement:
    # Складское движение меняет текущий остаток товара и сохраняет аудит операции.
    product = db.get(models.Product, movement_in.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if movement_in.movement_type == models.MovementType.INBOUND:
        product.quantity += movement_in.quantity
    elif movement_in.movement_type == models.MovementType.OUTBOUND:
        if product.quantity < movement_in.quantity:
            raise HTTPException(status_code=400, detail="Not enough stock for outbound movement")
        product.quantity -= movement_in.quantity
    else:
        product.quantity = movement_in.quantity

    movement = models.StockMovement(**movement_in.model_dump())
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


def create_order(
    db: Session, order_in: schemas.OrderCreate, created_by_id: int
) -> models.Order:
    # При создании заказа проверяем наличие каждого товара и достаточный остаток.
    order = models.Order(customer_name=order_in.customer_name, created_by_id=created_by_id)
    for item_in in order_in.items:
        product = db.get(models.Product, item_in.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item_in.product_id} not found")
        if product.quantity < item_in.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for product {product.sku}",
            )
        order.items.append(
            models.OrderItem(product_id=item_in.product_id, quantity=item_in.quantity)
        )
    db.add(order)
    db.commit()
    db.refresh(order)
    return get_order(db, order.id)


def get_order(db: Session, order_id: int) -> models.Order:
    order = (
        db.query(models.Order)
        .options(joinedload(models.Order.items))
        .filter(models.Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def update_order_status(
    db: Session, order: models.Order, status_value: models.OrderStatus
) -> models.Order:
    # Отгрузка списывает товары со склада и создает движения расхода.
    if order.status == status_value:
        return order

    if status_value == models.OrderStatus.SHIPPED:
        for item in order.items:
            product = db.get(models.Product, item.product_id)
            if not product or product.quantity < item.quantity:
                raise HTTPException(status_code=400, detail="Not enough stock to ship order")
        for item in order.items:
            product = db.get(models.Product, item.product_id)
            product.quantity -= item.quantity
            db.add(
                models.StockMovement(
                    product_id=item.product_id,
                    movement_type=models.MovementType.OUTBOUND,
                    quantity=item.quantity,
                    comment=f"Отгрузка заказа #{order.id} для {order.customer_name}",
                )
            )

    order.status = status_value
    db.commit()
    db.refresh(order)
    return get_order(db, order.id)
