from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_say_hello() -> None:
    response = client.get("/hello/deta")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello deta"}
