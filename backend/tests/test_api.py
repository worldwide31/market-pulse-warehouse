import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def test_client():
    with TestClient(app) as client:
        yield client


def auth(client: TestClient, username: str, password: str) -> dict[str, str]:
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_healthcheck(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_admin_can_read_products(test_client):
    response = test_client.get("/products", headers=auth(test_client, "admin", "admin123"))
    assert response.status_code == 200
    assert len(response.json()) >= 3


def test_clerk_cannot_create_product(test_client):
    response = test_client.post(
        "/products",
        headers=auth(test_client, "clerk", "clerk123"),
        json={
            "sku": "DENY-001",
            "name": "Denied product",
            "category": "Security",
            "location": "Z-01",
            "quantity": 1,
            "min_quantity": 0,
        },
    )
    assert response.status_code == 403


def test_invalid_role_is_rejected(test_client):
    response = test_client.post(
        "/users",
        headers=auth(test_client, "admin", "admin123"),
        json={
            "username": "badrole",
            "full_name": "Bad Role",
            "role": "owner",
            "password": "badrole123",
        },
    )
    assert response.status_code == 422


def test_order_rejects_excessive_quantity(test_client):
    products = test_client.get("/products", headers=auth(test_client, "admin", "admin123")).json()
    product_id = products[0]["id"]
    response = test_client.post(
        "/orders",
        headers=auth(test_client, "manager", "manager123"),
        json={
            "customer_name": "Acme Test",
            "items": [{"product_id": product_id, "quantity": 100000}],
        },
    )
    assert response.status_code == 400
