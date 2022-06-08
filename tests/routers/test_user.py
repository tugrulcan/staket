from random import randint
from typing import List

from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from requests import Response
from sqlalchemy.orm import Session

from app.models.user import User, UserCreate, UserDisplay
from app.routers.user import router as user_router


def test_user_creation(
    client: TestClient,
    session: Session,
    faker: Faker,
) -> None:
    user_create_payload: UserCreate = UserCreate(
        name=faker.name(),
        email=faker.email(),
        password=faker.password(),
        is_active=faker.pybool(),
    )
    response: Response = client.post(
        url=f"{user_router.prefix}/",
        json=user_create_payload.dict(),
    )

    assert response.status_code == status.HTTP_201_CREATED

    response_json = response.json()
    assert response_json["name"] == user_create_payload.name
    assert response_json["email"] == user_create_payload.email
    assert response_json["is_active"] == user_create_payload.is_active
    assert response_json["id"] is not None


def test_get_all_users(
    client: TestClient,
    session: Session,
    faker: Faker,
) -> None:
    users = insert_users(session=session, count=randint(1, 20), faker=faker)

    response: Response = client.get(url=f"{user_router.prefix}/")

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


def insert_users(
    session: Session,
    faker: Faker,
    count: int = 10,
) -> List[User]:
    user_create_payloads: List[UserCreate] = [
        UserCreate(
            name=faker.name(),
            email=faker.email(),
            password=faker.password(),
            is_active=faker.pybool(),
        )
        for _ in range(count)
    ]
    users: List[User] = session.query(User).all()
    assert len(users) == 0, "No users should be present"
    session.add(user_create_payloads[0])
    session.commit()
    session.add_all(user_create_payloads)
    session.commit()
    users: List[User] = session.query(User).all()
    assert len(users) == count, (
        "Number of users should match with the "
        "number of users inserted into the "
        "database "
    )
    return users


# @pytest.mark.asyncio
# async def insert_users(number_of_users: int = 10) -> List[User]:
#     session: AsyncSession = await get_session().__anext__()
#
#     fake = Faker()
#     user_create_payloads: List[UserCreate] = [
#         UserCreate(
#             name=fake.name(),
#             email=fake.email(),
#             password=fake.password(),
#             is_active=fake.pybool(),
#         )
#         for _ in range(number_of_users)
#     ]
#     # await create_db_and_tables(async_engine=session.bind)
#
#     result = await session.execute(select(User))
#     users: List[User] = result.scalars().all()
#     assert len(users) == 0, "No users should be present"
#
#     # Insert users in user_create_payloads list
#     for user_create_payload in user_create_payloads:
#         await session.execute(
#             User.__table__.insert().values(**user_create_payload.dict())
#         )
#     result = await session.execute(select(User))
#     await session.commit()
#     users: List[User] = result.scalars().all()
#
#     assert len(users) == number_of_users, (
#         "Number of users should match with the "
#         "number of users inserted into the "
#         "database "
#     )
#
#     return users
#
#
# @pytest.mark.asyncio
# async def test_get_user_by_id() -> None:
#     users = await insert_users()
#     user: User = users[randint(0, len(users) - 1)]
#
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.get(url=f"{user_router.prefix}/{user.id}")
#     assert response.status_code == status.HTTP_200_OK
#
#     response_json = response.json()
#     response_user: UserDisplay = UserDisplay(**response_json)
#     assert response_user == UserDisplay(
#         **user.dict()
#     ), "User in response should match with the user in the database"
