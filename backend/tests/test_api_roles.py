from conftest import auth


# Проверка ролевой модели: кладовщик не может создавать товары.
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


# Проверка серверной валидации: неизвестная роль отклоняется.
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
