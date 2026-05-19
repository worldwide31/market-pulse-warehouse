from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload

from . import crud, models, schemas
from .config import AUTO_SEED
from .database import Base, engine, get_db, wait_for_database
from .security import create_token, get_current_user, require_roles, verify_password
from .seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Инициализация инфраструктуры при старте приложения: ждем PostgreSQL,
    # создаем таблицы и добавляем демонстрационные данные.
    wait_for_database()
    Base.metadata.create_all(bind=engine)
    if AUTO_SEED:
        seed_database()
    yield


app = FastAPI(
    title="Warehouse and Orders API",
    description="CRUD API for warehouse inventory, orders and role-based access control.",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    # CORS нужен, чтобы статический frontend мог обращаться к API из браузера.
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login", response_model=schemas.Token)
def login(login_in: schemas.LoginRequest, db: Session = Depends(get_db)):
    # Проверка пары логин/пароль и выдача bearer-токена для последующих запросов.
    user = db.query(models.User).filter(models.User.username == login_in.username).first()
    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {
        "access_token": create_token(user.id),
        "role": user.role,
    }


@app.get("/me", response_model=schemas.UserRead)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.get("/users", response_model=list[schemas.UserRead])
def list_users(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles(models.Role.ADMIN)),
):
    # Управление пользователями доступно только администратору.
    return db.query(models.User).order_by(models.User.id).all()


@app.post("/users", response_model=schemas.UserRead, status_code=201)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles(models.Role.ADMIN)),
):
    return crud.create_user(db, user_in)


@app.patch("/users/{user_id}", response_model=schemas.UserRead)
def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles(models.Role.ADMIN)),
):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db, user, user_in)


@app.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(models.Role.ADMIN)),
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()


@app.get("/products", response_model=list[schemas.ProductRead])
def list_products(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    # Каталог товаров виден всем авторизованным пользователям.
    return db.query(models.Product).order_by(models.Product.id).all()


@app.post("/products", response_model=schemas.ProductRead, status_code=201)
def create_product(
    product_in: schemas.ProductCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles(models.Role.ADMIN, models.Role.MANAGER)),
):
    return crud.create_product(db, product_in)


@app.patch("/products/{product_id}", response_model=schemas.ProductRead)
def update_product(
    product_id: int,
    product_in: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles(models.Role.ADMIN, models.Role.MANAGER)),
):
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in product_in.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@app.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles(models.Role.ADMIN, models.Role.MANAGER)),
):
    # Перед удалением товара очищаем связанные движения и позиции заказов,
    # чтобы не нарушить внешние ключи в PostgreSQL.
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    affected_order_ids = [
        order_id
        for (order_id,) in db.query(models.OrderItem.order_id)
        .filter(models.OrderItem.product_id == product_id)
        .distinct()
        .all()
    ]
    db.query(models.StockMovement).filter(models.StockMovement.product_id == product_id).delete()
    db.query(models.OrderItem).filter(models.OrderItem.product_id == product_id).delete()
    for order_id in affected_order_ids:
        has_items = (
            db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).first()
            is not None
        )
        if not has_items:
            order = db.get(models.Order, order_id)
            if order:
                db.delete(order)
    db.delete(product)
    db.commit()


@app.get("/movements", response_model=list[schemas.MovementRead])
def list_movements(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    # История движений отдается вместе с данными товара для понятного интерфейса.
    return (
        db.query(models.StockMovement)
        .options(joinedload(models.StockMovement.product))
        .order_by(models.StockMovement.id.desc())
        .limit(100)
        .all()
    )


@app.post("/movements", response_model=schemas.MovementRead, status_code=201)
def create_movement(
    movement_in: schemas.MovementCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles(models.Role.ADMIN, models.Role.MANAGER)),
):
    return crud.apply_movement(db, movement_in)


@app.delete("/movements/{movement_id}", status_code=204)
def delete_movement(
    movement_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles(models.Role.ADMIN, models.Role.MANAGER)),
):
    movement = db.get(models.StockMovement, movement_id)
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")
    db.delete(movement)
    db.commit()


@app.get("/orders", response_model=list[schemas.OrderRead])
def list_orders(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    # Заказы отдаются с позициями и вложенными товарами, чтобы frontend не
    # показывал оператору технические product_id.
    return (
        db.query(models.Order)
        .options(joinedload(models.Order.items).joinedload(models.OrderItem.product))
        .order_by(models.Order.id.desc())
        .all()
    )


@app.post("/orders", response_model=schemas.OrderRead, status_code=201)
def create_order(
    order_in: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_order(db, order_in, current_user.id)


@app.patch("/orders/{order_id}", response_model=schemas.OrderRead)
def update_order(
    order_id: int,
    order_in: schemas.OrderUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles(models.Role.ADMIN, models.Role.MANAGER)),
):
    order = crud.get_order(db, order_id)
    if order_in.customer_name is not None:
        order.customer_name = order_in.customer_name
    if order_in.status is not None:
        return crud.update_order_status(db, order, order_in.status)
    db.commit()
    return crud.get_order(db, order_id)


@app.delete("/orders/{order_id}", status_code=204)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles(models.Role.ADMIN, models.Role.MANAGER)),
):
    order = crud.get_order(db, order_id)
    db.delete(order)
    db.commit()
