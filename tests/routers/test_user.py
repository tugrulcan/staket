from typing import List

import pytest

from faker import Faker
from fastapi import status
from httpx import AsyncClient

from app.main import app
from app.models import UserCreate
from app.routers.user import router as user_router


@pytest.mark.asyncio
async def test_user_creation() -> None:
    fake = Faker()
    user_create_payload: UserCreate = UserCreate(
        name=fake.name(),
        email=fake.email(),
        password=fake.password(),
        is_active=fake.pybool(),
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            url=f"{user_router.prefix}/", json=user_create_payload.dict()
        )
    assert response.status_code == status.HTTP_201_CREATED

    response_json = response.json()
    assert response_json["name"] == user_create_payload.name
    assert response_json["email"] == user_create_payload.email
    assert response_json["is_active"] == user_create_payload.is_active
    assert response_json["id"] is not None


@pytest.mark.asyncio
async def test_get_all_users() -> None:

    fake = Faker()
    user_create_payloads: List[UserCreate] = [
        UserCreate(
            name=fake.name(),
            email=fake.email(),
            password=fake.password(),
            is_active=fake.pybool(),
        )
        for _ in range(10)
    ]

    async with AsyncClient(app=app, base_url="http://test") as ac:
        for user_create_payload in user_create_payloads:
            response = await ac.post(
                url=f"{user_router.prefix}/", json=user_create_payload.dict()
            )
            assert response.status_code == status.HTTP_201_CREATED

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(url=f"{user_router.prefix}/")
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert len(response_json) == len(user_create_payloads)
    for index, user_create_payload in user_create_payloads:
        assert response_json[index]["name"] == user_create_payload.name
        assert response_json[index]["email"] == user_create_payload.email
        assert (
            response_json[index]["is_active"] == user_create_payload.is_active
        )
        assert response_json[index]["id"] is not None
