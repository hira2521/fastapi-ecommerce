from fastapi.testclient import TestClient

def test_register_user(client: TestClient):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "testpassword"
        }   
    )
    
    assert response.status_code == 200
    assert 'message' in response.json()

def test_register_and_login(client: TestClient):
    register_response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "testpassword"
        }
    )
    assert register_response.status_code == 200

    response = client.post(
        "/auth/login",
        data={
            "username": "testuser@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_incorrect_password(client: TestClient):
    response = client.post(
        "/auth/login",
        data={
            "username": "admin@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."

#only admin can create products
def test_create_product(client: TestClient, admin_token):
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

def test_delete_product(client: TestClient, admin_token, create_product):
    response = client.delete(
        "/products/1",
        headers = admin_token
        )
    
    assert response.status_code == 200
    assert "successfully deleted" in response.json()["message"].lower()

    #additional check to ensure product is gone
    get_response = client.get("/products/1")
    assert get_response.status_code == 404

def test_place_order(client: TestClient, user_token, create_product):  
    response = client.post(
        "/orders",
        json={
            "items": [
                {"product_id": 1, "quantity": 2}
            ]
        },
        headers=user_token
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Order placed successfully."

#only admin can view all orders
def test_list_orders(client: TestClient, admin_token):  
    response = client.get(
        "/orders",
        headers=admin_token
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_cannot_list_orders_as_user(client: TestClient, user_token):
    response = client.get(
        "/orders",
        headers=user_token
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin privileges required"

def test_place_and_pay_order(client: TestClient, user_token, create_product):
    # Place order
    place_response = client.post(
        "/orders",
        json={
            "items": [
                {"product_id": 1, "quantity": 2}
            ]
        },
        headers=user_token
    )
    assert place_response.status_code == 200
    assert place_response.json()["message"] == "Order placed successfully."

    order_id = place_response.json()["order_id"]

    # Pay for the order
    pay_response = client.post(
        f"/orders/{order_id}/pay",
        headers=user_token
    )
    assert pay_response.status_code == 200
    assert pay_response.json()["message"] == f"Order {order_id} paid successfully."

def test_update_order_status(client: TestClient, admin_token, user_token, create_product):
    # Place order as user
    place_response = client.post(
        "/orders",
        json={
            "items": [
                {"product_id": 1, "quantity": 2}
            ]
        },
        headers=user_token
    )
    assert place_response.status_code == 200
    assert place_response.json()["message"] == "Order placed successfully."

    order_id = place_response.json()["order_id"]

    # Try to update order status as user (should fail)
    update_response = client.patch(
        f"/orders/{order_id}/status",
        json={"status": "shipped"},
        headers=user_token
    )
    assert update_response.status_code == 403
    assert update_response.json()["detail"] == "Admin privileges required"

    # Update order status as admin
    update_response = client.patch(
        f"/orders/{order_id}/status",
        json={"status": "shipped"},
        headers=admin_token
    )
    assert update_response.status_code == 200
    assert update_response.json()["message"] == f"Order {order_id} status updated to shipped."