from random import randint
from sqlalchemy import select
from typing import List

import pytest
from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from requests import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from httpx import AsyncClient

from app.models.user import User, UserCreate, UserDisplay
from app.routers.user import router as user_router


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
async def test_get_all_users(
        client: TestClient,
        session: AsyncSession,
        faker: Faker,
) -> None:
    users = await insert_users(session=session, count=randint(1, 20), fake=faker)

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


# def insert_users(
#     session: Session,
#     faker: Faker,
#     count: int = 10,
# ) -> List[User]:
#     user_create_payloads: List[UserCreate] = [
#         UserCreate(
#             name=faker.name(),
#             email=faker.email(),
#             password=faker.password(),
#             is_active=faker.pybool(),
#         )
#         for _ in range(count)
#     ]
#     users: List[User] = session.query(User).all()
#     assert len(users) == 0, "No users should be present"
#     session.add(user_create_payloads[0])
#     session.commit()
#     session.add_all(user_create_payloads)
#     session.commit()
#     users: List[User] = session.query(User).all()
#     assert len(users) == count, (
#         "Number of users should match with the "
#         "number of users inserted into the "
#         "database "
#     )
#     return users


@pytest.mark.asyncio
async def insert_users(
        session: AsyncSession,
        count: int = 10,
        fake: Faker = Faker(),
) -> List[User]:
    # session: AsyncSession = await session

    user_create_payloads: List[UserCreate] = [
        UserCreate(
            name=fake.name(),
            email=fake.email(),
            password=fake.password(),
            is_active=fake.pybool(),
        )
        for _ in range(count)
    ]
    # await create_db_and_tables(async_engine=session.bind)
    result = await session.execute(select(User))
    users: List[User] = result.scalars().all()
    assert len(users) == 0, "No users should be present"

    # Insert users in user_create_payloads list
    for user_create_payload in user_create_payloads:
        await session.execute(
            User.__table__.insert().values(**user_create_payload.dict())
        )
    result = await session.execute(select(User))
    await session.commit()
    users: List[User] = result.scalars().all()

    assert len(users) == count, (
        "Number of users should match with the "
        "number of users inserted into the "
        "database "
    )

    return users
