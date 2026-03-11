from pydantic import BaseModel
from .models import OrderStatus

class CreateProductRequest(BaseModel):
    product_id: int
    name: str
    price: float
    stock: int

class CartItemRequest(BaseModel):
    product_id: int
    quantity: int

class PlaceOrderRequest(BaseModel):
    items: list[CartItemRequest]

class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus

class RegisterUserRequest(BaseModel):
    name: str
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"