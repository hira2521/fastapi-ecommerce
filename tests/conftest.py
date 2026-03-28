import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app
from app.models import Base, UserDB
from app.auth import hash_password

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(autouse=True) 
def setup_db():
    Base.metadata.drop_all(bind=engine) #drop all tables to start with a clean slate for testing
    Base.metadata.create_all(bind=engine) #recreate all tables from models

    db = TestingSessionLocal()
    
    try:
        admin = UserDB(
        id=1,
        name="Admin",
        email="admin@example.com",
        password_hash=hash_password("adminpassword"),
        is_admin=True
    )
        db.add(admin)
        db.commit()
        yield
    finally:
        db.close()

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to override the get_db dependency with our test database
@pytest.fixture()
def client():
    app.dependency_overrides[get_db] = override_get_db 
    with TestClient(app) as c:
        yield c 
    app.dependency_overrides.clear() #clear the overrides after the test is done


#admin token fixture for tests to login as admin
@pytest.fixture
def admin_token(client: TestClient):
    login_response = client.post(
        "/auth/login",
        data={
            "username": "admin@example.com",
            "password": "adminpassword"
        }
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers

#user token fixture for tests to login as regular user
@pytest.fixture
def user_token(client: TestClient):
    register_response = client.post(
        "/auth/register",
        json={
            "name": "User Token",
            "email": "usertoken@example.com",
            "password": "userpassword"}
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        data={
            "username": "usertoken@example.com",
            "password": "userpassword"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers

#product token for creating product
@pytest.fixture
def create_product(client: TestClient, admin_token):
    response = client.post(
        "/products",
        json={
            "product_id": 1,
            "name": "Test Product",
            "price": 9.99,
            "stock": 100
        },
        headers=admin_token
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Product created successfully."