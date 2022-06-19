from fastapi.testclient import TestClient
from requests import Response
from starlette import status

from app.main import app

client = TestClient(app)


def test_root() -> None:
    response: Response = client.get("/", allow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.is_redirect is True
    assert response.next is not None
    assert (
        response.next.url == client.base_url + "/docs"
    ), "Does not redirect to docs"


def test_db_ready() -> None:
    response: Response = client.get("/db_ready")
    assert response.status_code == 200
    assert response.content == b"Database is ready."
