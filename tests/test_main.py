import pytest

from fastapi import status
from httpx import AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_root() -> None:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/", follow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.is_redirect is True
    assert response.next_request is not None
    assert response.next_request.url == ac.base_url.__str__() + "/docs"


@pytest.mark.anyio
async def test_db_ready() -> None:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/db_ready")
    assert response.status_code == 200
    assert response.content == b"Database is ready."
