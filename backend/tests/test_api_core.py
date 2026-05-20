from conftest import auth


# Базовая проверка доступности API.
def test_healthcheck(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# Проверка чтения товаров авторизованным администратором.
def test_admin_can_read_products(test_client):
    response = test_client.get("/products", headers=auth(test_client, "admin", "admin123"))
    assert response.status_code == 200
    assert len(response.json()) >= 3
