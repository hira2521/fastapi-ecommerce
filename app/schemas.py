from pydantic import BaseModel, Field, field_validator
from .models import OrderStatus

class CreateProductRequest(BaseModel):
    product_id: int = Field(gt=0)
    name: str = Field(min_length=1)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)

class CartItemRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)

class PlaceOrderRequest(BaseModel):
    items: list[CartItemRequest]

class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus

class RegisterUserRequest(BaseModel):
    name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    password: str = Field(min_length=8)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    