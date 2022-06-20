import pytest

from faker import Faker
from fastapi.testclient import TestClient
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_root(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.get(
            url="/",
        )

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.is_redirect is True
    assert response.next_request is not None
    assert (
        response.next_request.url == "http://test/docs"
    ), "Does not redirect to docs"


@pytest.mark.asyncio
async def test_db_ready(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.get(
            url="/db_ready",
        )
    assert response.status_code == status.HTTP_200_OK
    assert response.content == b"Database is ready."
