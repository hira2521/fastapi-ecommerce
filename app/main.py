from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from .schemas import RegisterUserRequest
from .auth import (get_current_user, create_access_token, require_admin)
from .database import Base, engine, get_db
from .schemas import (
    CreateProductRequest,
    RegisterUserRequest,
    PlaceOrderRequest,
    UpdateOrderStatusRequest,
)
from .models import OrderStatus, ProductDB, UserDB, OrderDB, OrderItemDB
from . import crud


app = FastAPI()

# ------PRODUCTS------
@app.post("/products")
def create_product(
    request: CreateProductRequest, 
    db: Session = Depends(get_db),
    admin: UserDB = Depends(require_admin),
):  
    product = crud.create_product(db, request.product_id, request.name, request.price, request.stock)
    return {
        "message": f"Product created successfully.",
        "product_id": product.product_id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock
    }

@app.get("/products")
def list_products(db: Session = Depends(get_db)):
    products = crud.list_products(db)
    return [
        {
            "product_id": p.product_id,
            "name": p.name,
            "price": p.price,
            "stock": p.stock
        }
        for p in products
    ]

@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    return {
        "product_id": product.product_id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock
    }

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), admin: UserDB = Depends(require_admin)):
    crud.delete_product(db, product_id)
    return {
        "message": f"Product ID: {product_id} successfully deleted."
    }
    
# ---------- ORDERS ----------
@app.post("/orders")
def place_order(request: PlaceOrderRequest, db: Session = Depends(get_db), user: UserDB = Depends(get_current_user)):
    order = crud.place_order(db, user.email, request.items)
    return {
        "message": f"Order placed successfully.",
        "order_id": order.order_id,
        "total_price": order.total_price,
        "status": order.status
    }
        
    
@app.get("/orders/me")
def list_my_orders(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    orders = crud.list_user_orders(db, current_user.email)
    return [
            {
                "order_id": o.order_id,
                "total_price": o.total_price,
                "status": o.status,
                "created_at": o.created_at,
                "items": [
                    {
                        "product_id": i.product_id,
                        "quantity": i.quantity,
                        "price": i.price
                    }
                    for i in o.items
                ]
            }
            for o in orders
    ]
      
#admin only
@app.get("/orders")
def list_orders(db: Session = Depends(get_db), admin: UserDB = Depends(require_admin)):
    orders = crud.list_orders(db)
    return [
            {
                "order_id": o.order_id,
                "email": o.email,
                "total_price": o.total_price,
                "status": o.status,
                "created_at": o.created_at,
                "items": [
                    {
                        "product_id": i.product_id,
                        "quantity": i.quantity,
                        "price": i.price
                    }
                    for i in o.items
                ]
            }
            for o in orders
    ]

#admin order search only
@app.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db), admin: UserDB = Depends(require_admin)):
    order = crud.get_order(db, order_id)
    return {    
            "order_id": order.order_id,
            "email": order.email,
            "total_price": order.total_price,
            "status": order.status,
            "created_at": order.created_at,
            "items": [
                {
                    "product_id": i.product_id,
                    "quantity": i.quantity,
                    "price": i.price
                }
                for i in order.items
            ]
        }

#admin can update order status only
@app.patch("/orders/{order_id}/status")
def update_order_status(order_id: int, request: UpdateOrderStatusRequest, db: Session = Depends(get_db), admin: UserDB = Depends(require_admin)):
    order = crud.update_order_status(db, order_id, request.status)
    return {
        "message": f"Order {order.order_id} status updated to {order.status}."
    }
@app.post("/orders/{order_id}/pay")
def pay_order(
    order_id: int, 
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
    ):
    
    order = crud.pay_order(db, order_id, current_user)
    return {
        "message": f"Order {order.order_id} paid successfully."
    }


@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    order = crud.cancel_order(db, order_id, current_user)
    return {
        "message": f"Order {order.order_id} cancelled successfully."
    }

# ---------- AUTH ----------
@app.post("/auth/register")
def register(request: RegisterUserRequest, db: Session = Depends(get_db)):
    user = crud.register_user(db, request.name, request.email, request.password)
    return {
        "message": f"User Registered with email {user.email}."
    }

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    email = form_data.username
    password = form_data.password
    
    user = crud.authenticate_user(db, email, password)
    token = create_access_token(user_email=user.email)
    
    return {"access_token": token, "token_type": "bearer"}