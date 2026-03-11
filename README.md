# FastAPI E-Commerce Backend

This project is a RESTful backend API for an e-commerce store built with FastAPI, SQLAlchemy, and JWT authentication. The system supports user registration, authentication, product management, and order processing with role-based access control for administrators.

The project demonstrates backend development concepts including API design, authentication and authorization, relational database modeling, transactional order processing, and automated API testing.

## Installation

Follow these steps to run the project locally.

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ecommerce_store.git
cd ecommerce_store
```

### 2. Create a virtual environment

Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the database

The SQLite database will be created automatically when the application starts.

### 5. Create the admin user

Run the script below to create the default admin account.

```bash
python app/create_admin.py
```

Default admin credentials:
Email: admin@example.com
Password: adminpassword


### 6. Start the FastAPI server

```bash
uvicorn app.main:app --reload
```

### 7. Access the API documentation

Open the following URL in your browser:

```
http://127.0.0.1:8000/docs
```

This opens the automatically generated Swagger UI where you can test all API endpoints.


## Features

### Authentication
- User registration
- Password hashing using bcrypt
- JWT token authentication
- Token-based authorization for protected endpoints
- Role-based admin access control

### Products
- Admin-only product creation
- Retrieve product by ID
- List all products

### Orders
- Users can place orders containing multiple items
- Product stock validation
- Automatic total price calculation
- Users can view their own orders

### Order Management
Users can:
- Pay for their own orders
- Cancel their own orders

Administrators can:
- View all orders
- Search orders by ID
- Update order status

### Testing

Automated API tests are implemented using pytest and FastAPI TestClient.

The test suite currently covers:
- User registration
- User login
- Invalid login credentials
- Admin authorization
- Product creation
- Order placement
- Order payment
- Order status updates

## Technology Stack

**Framework**
- FastAPI

**Database**
- SQLite

**ORM**
- SQLAlchemy

**Authentication**
- JWT (python-jose)

**Password Hashing**
- Passlib with bcrypt

**Testing**
- pytest
- FastAPI TestClient

---

## Project Structure

- main.py contains the FastAPI application and API endpoints
- crud.py contains business logic and database operations
- models.py defines the SQLAlchemy database models
- schemas.py defines the Pydantic request models
- auth.py handles authentication logic including JWT creation and verification
- database.py configures the database engine and session management

## Authentication Flow
1. A user registers with an email and password.
2. The password is hashed using bcrypt before storage.
3. The user logs in with their credentials.
4. The server returns a JWT access token.
5. The client sends the token in the Authorization header when making protected requests


# API Endpoints

## Authentication
- POST /auth/register
    - Register a new user.
- POST /auth/login
    - Authenticate a user and return a JWT token.

## Products
- POST /products
    - Create a new product (admin only).
- GET /products
    - Retrieve all products.
- GET /products/{product_id}
    - Retrieve a specific product.

## Orders
- POST /orders
    - Place a new order.
- GET /orders/me
    - Retrieve the current user’s orders.
- GET /orders
    - Retrieve all orders (admin only).
- GET /orders/{order_id}
    - Retrieve a specific order (admin only).
- PATCH /orders/{order_id}/status
    - Update order status (admin only).
- POST /orders/{order_id}/pay
    - Pay for an order.
- POST /orders/{order_id}/cancel
    - Cancel an order.

