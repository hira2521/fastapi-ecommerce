from fastapi import HTTPException
from sqlalchemy.orm import Session
from .schemas import CartItemRequest
from .models import ProductDB, UserDB, OrderDB, OrderItemDB, OrderStatus
from .auth import hash_password, verify_password

def create_product(db: Session, product_id: int, name: str, price: float, stock: int):
    existing = db.query(ProductDB).filter(ProductDB.product_id == product_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Product with id {product_id} already exists.")

    product = ProductDB(product_id=product_id, name=name, price=price, stock=stock)
    db.add(product)
    db.commit()
    return product


def list_products(db: Session):
    return db.query(ProductDB).all()

def get_product(db: Session, product_id: int):
    product = db.query(ProductDB).filter(ProductDB.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found.")
    return product

def delete_product(db: Session, product_id):
    product = db.query(ProductDB).filter(ProductDB.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found.")
    
    db.delete(product)
    db.commit()
    return None
#-------ORDERS----------

def place_order(db: Session, email: str, items: list[CartItemRequest]):
    # 1) user exists?
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail=f"User with email {email} not found.")
    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty.")

    # 2) create order once
    order = OrderDB(email=email, status=OrderStatus.pending.value, total_price=0.0)
    db.add(order) 
    db.flush() #Will allow for order ID to be auto generated so we can use it to create order items object.
    
    total_price = 0.0

    # 3) for each item: check product, check stock, reduce stock, create OrderItemDB
    for item in items:
        product_id = item.product_id
        quantity = item.quantity

        if quantity <= 0:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Quantity must be positive for product {product_id}.")

        #find the product to get price and stock
        product = db.query(ProductDB).filter(ProductDB.product_id == product_id).first()

        #validate and check for product and stock
        if not product:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Product {product_id} not found.")

        if product.stock < quantity:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product_id}. Available: {product.stock}")

        # reduce stock by the quantity in order
        product.stock -= quantity

        # snapshot price at purchase time
        item_price = product.price

        # create order item row for each product in the order
        order_item = OrderItemDB(
            order_id=order.order_id,
            product_id=product_id,
            quantity=quantity,
            price=item_price,
        )
        total_price += item_price * quantity
        db.add(order_item)

    # 4) save order total
    order.total_price = total_price

    # 5) commit once at the end, save everything
    db.commit()

    return order

def list_user_orders(db: Session, email: str):
    return db.query(OrderDB).filter(OrderDB.email == email).all()

def list_orders(db: Session):
    return db.query(OrderDB).all()

def list_users(db: Session):
    return db.query(UserDB).all()

def get_order(db: Session, order_id: int):
    order = db.query(OrderDB).filter(OrderDB.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found.")
    return order

def update_order_status(db: Session, order_id: int, new_status: OrderStatus):
    order = db.query(OrderDB).filter(OrderDB.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")

    order.status = new_status.value
    db.commit()
    return order

def pay_order(db: Session, order_id: int, current_user: UserDB):
    order = db.query(OrderDB).filter(OrderDB.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")
  
    if order.email != current_user.email:
        raise HTTPException(status_code=403, detail=f"Order {order_id} belongs to a different user. Must be logged in as the correct user.")

    if order.status != OrderStatus.pending.value:
        raise HTTPException(status_code=400, detail=f"Order {order_id} must be Pending to pay.")

    order.status = OrderStatus.paid.value
    db.commit()
    return order

def cancel_order(db: Session, order_id: int, current_user: UserDB):
    order = db.query(OrderDB).filter(OrderDB.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")

    if order.email != current_user.email:
        raise HTTPException(status_code=403, detail=f"Order {order_id} belongs to a different user. Must be logged in as the correct user.")

    if order.status == OrderStatus.cancelled.value:
        raise HTTPException(status_code=400, detail=f"Order {order_id} already cancelled.")

    order.status = OrderStatus.cancelled.value
    db.commit()
    return order

def register_user(db: Session, name: str, email: str, password: str):
    if db.query(UserDB).filter(UserDB.email == email).first():
        raise HTTPException(status_code=400, detail=f"Email {email} already registered.")

    pw_hash = hash_password(password)

    user = UserDB(
        name=name,
        email=email,
        password_hash=pw_hash
    )
    db.add(user)
    db.commit()
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail=f"Invalid email or password.")
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return user