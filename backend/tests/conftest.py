import pytest
from fastapi.testclient import TestClient

from app.main import app


# Общие фикстуры тестов: создают тестовый HTTP-клиент FastAPI.
@pytest.fixture()
def test_client():
    with TestClient(app) as client:
        yield client


# Общий helper авторизации: возвращает Bearer-заголовок для защищенных API.
def auth(client: TestClient, username: str, password: str) -> dict[str, str]:
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
