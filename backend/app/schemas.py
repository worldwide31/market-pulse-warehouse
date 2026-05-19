from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import MovementType, OrderStatus, Role


class Token(BaseModel):
    # Ответ авторизации: токен и роль нужны frontend для настройки интерфейса.
    access_token: str
    token_type: str = "bearer"
    role: Role


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_.-]+$")
    full_name: str = Field(min_length=2, max_length=128)
    role: Role


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=128)
    role: Role | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class ProductBase(BaseModel):
    # Валидация товара отсекает отрицательные остатки и неправильный формат SKU.
    sku: str = Field(min_length=2, max_length=32, pattern=r"^[A-Z0-9-]+$")
    name: str = Field(min_length=2, max_length=128)
    category: str = Field(min_length=2, max_length=64)
    location: str = Field(min_length=1, max_length=32)
    quantity: int = Field(ge=0)
    min_quantity: int = Field(ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=128)
    category: str | None = Field(default=None, min_length=2, max_length=64)
    location: str | None = Field(default=None, min_length=1, max_length=32)
    quantity: int | None = Field(default=None, ge=0)
    min_quantity: int | None = Field(default=None, ge=0)


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class MovementCreate(BaseModel):
    # Входная схема движения ограничивает количество и тип операции.
    product_id: int
    movement_type: MovementType
    quantity: int = Field(gt=0, le=100000)
    comment: str = Field(default="", max_length=500)


class MovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product: ProductRead | None = None
    movement_type: MovementType
    quantity: int
    comment: str
    created_at: datetime


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, le=100000)


class OrderCreate(BaseModel):
    # Заказ должен содержать хотя бы одну позицию.
    customer_name: str = Field(min_length=2, max_length=128)
    items: list[OrderItemCreate] = Field(min_length=1, max_length=50)


class OrderUpdate(BaseModel):
    customer_name: str | None = Field(default=None, min_length=2, max_length=128)
    status: OrderStatus | None = None


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product: ProductRead | None = None
    quantity: int


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    status: OrderStatus
    created_by_id: int
    created_at: datetime
    items: list[OrderItemRead]
