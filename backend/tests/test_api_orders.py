from conftest import auth


# Проверка бизнес-правила: заказ не может списать больше товара, чем есть на складе.
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
