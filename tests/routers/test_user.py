from random import randint
from typing import List

import pytest

from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient
from requests import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserCreate, UserDisplay
from app.routers.user import router as user_router
from tests.conftest import insert_users


@pytest.mark.asyncio
async def test_user_creation(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    user_create_payload: UserCreate = UserCreate(
        name=faker.name(),
        email=faker.email(),
        password=faker.password(),
        is_active=faker.pybool(),
    )
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.post(
            url=f"{user_router.prefix}/",
            json=user_create_payload.dict(),
        )

    assert response.status_code == status.HTTP_201_CREATED

    response_json = response.json()
    assert response_json["name"] == user_create_payload.name
    assert response_json["email"] == user_create_payload.email
    assert response_json["is_active"] == user_create_payload.is_active
    assert response_json["id"] is not None


@pytest.mark.asyncio
async def test_user_creation_with_existing_email(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    users: List[User] = await insert_users(
        session=session, count=1, fake=faker
    )
    user_create_payload: UserCreate = UserCreate(
        name=faker.name(),
        email=users[0].email,
        password=faker.password(),
        is_active=faker.pybool(),
    )
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.post(
            url=f"{user_router.prefix}/",
            json=user_create_payload.dict(),
        )
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_get_all_users(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    users = await insert_users(
        session=session, count=randint(1, 20), fake=faker
    )

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.get(url=f"{user_router.prefix}/")

    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert len(response_json) == len(
        users
    ), "Number of users should match with the number of users in the database"

    for u in response_json:
        user_in_response: UserDisplay = UserDisplay(**u)
        user_in_db: UserDisplay = next(
            UserDisplay(**user.dict())
            for user in users
            if user.id == user_in_response.id
        )
        assert (
            user_in_response == user_in_db
        ), "User in response should match with the user in the database"


@pytest.mark.asyncio
async def test_get_user(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    users: List[User] = await insert_users(
        session=session, count=1, fake=faker
    )
    user: UserDisplay = UserDisplay(**users[0].dict())

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.get(
            url=f"{user_router.prefix}/{user.id}"
        )

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == user.dict()


@pytest.mark.asyncio
async def test_get_non_existing_user(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.get(
            url=f"{user_router.prefix}/{randint(1, 100)}"
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_user(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    users: List[User] = await insert_users(
        session=session, count=1, fake=faker
    )
    user: UserDisplay = UserDisplay(**users[0].dict())

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.delete(
            url=f"{user_router.prefix}/{user.id}"
        )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Query DB to check if user was deleted
    result = await session.execute(select(User))
    users_in_db: List[User] = result.scalars().all()
    assert len(users_in_db) == 0, "No users should be present"


@pytest.mark.asyncio
async def test_delete_non_existing_user(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.delete(
            url=f"{user_router.prefix}/{randint(1, 100)}"
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND
