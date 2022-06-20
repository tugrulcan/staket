from random import randint
from typing import List

import faker_commerce
import pytest

from faker import Faker
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.testclient import TestClient

from app.models.category import Category, CategoryCreate, CategoryDisplay
from app.routers.category import router as category_router
from tests.conftest import insert_categories


@pytest.mark.asyncio
async def test_get_non_existing_category(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.get(
            url=f"{category_router.prefix}/{randint(1, 100)}"
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_category(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    categories: List[Category] = await insert_categories(
        session=session, count=1, fake=faker
    )
    category: CategoryDisplay = CategoryDisplay(**categories[0].dict())

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.get(
            url=f"{category_router.prefix}/{category.id}"
        )

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == category.dict()


@pytest.mark.asyncio
async def test_get_all_categories(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    category_count = randint(3, 82)
    categories_in_db: List[Category] = await insert_categories(
        session=session, count=category_count, fake=faker
    )

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.get(
            url=f"{category_router.prefix}/?limit={category_count+1}"
        )

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert (
        len(response_json) == category_count
    ), "Response should contain all categories"
    for c in response_json:
        category_in_response: CategoryDisplay = CategoryDisplay(**c)
        category_in_db: CategoryDisplay = next(
            CategoryDisplay(**category.dict())
            for category in categories_in_db
            if category.id == category_in_response.id
        )
        assert category_in_response == category_in_db, (
            "Category in response should match "
            "with the category in the database"
        )

    @pytest.mark.asyncio
    async def test_category_creation(
        client: TestClient,
        session: AsyncSession,
        faker: Faker,
    ) -> None:
        faker.add_provider(faker_commerce.Provider)

        category_create_payload: CategoryCreate = CategoryCreate(
            name=faker.ecommerce_category(),
        )
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response: Response = await ac.post(
                url=f"{category_router.prefix}/",
                json=category_create_payload.dict(),
            )
        assert response.status_code == status.HTTP_201_CREATED
        response_json = response.json()
        assert (
            response_json["name"] == category_create_payload.name
        ), "Name should match"
        assert response_json["id"] is not None, "Id should be present"


@pytest.mark.asyncio
async def test_category_create(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    faker.add_provider(faker_commerce.Provider)

    category_create_payload: CategoryCreate = CategoryCreate(
        name=faker.ecommerce_category(),
    )
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.post(
            url=f"{category_router.prefix}/",
            json=category_create_payload.dict(),
        )
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert (
        response_json["name"] == category_create_payload.name
    ), "Name should match"
    assert response_json["id"] is not None, "Id should be present"


@pytest.mark.asyncio
async def test_creating_existing_category(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    categories = await insert_categories(session=session, count=1, fake=faker)
    category_create_payload: CategoryCreate = CategoryCreate(
        name=categories[0].name,
    )
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.post(
            url=f"{category_router.prefix}/",
            json=category_create_payload.dict(),
        )
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_category_update(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    categories = await insert_categories(session=session, count=1, fake=faker)
    category_update_payload: CategoryCreate = CategoryCreate(
        name=faker.ecommerce_category(),
    )
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.put(
            url=f"{category_router.prefix}/{categories[0].id}",
            json=category_update_payload.dict(),
        )
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert (
        response_json["name"] == category_update_payload.name
    ), "Name should match"
    assert response_json["id"] == categories[0].id, "Id should match"


@pytest.mark.asyncio
async def test_category_delete(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    categories = await insert_categories(session=session, count=1, fake=faker)
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.delete(
            url=f"{category_router.prefix}/{categories[0].id}",
        )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_category_delete_non_existing(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.delete(
            url=f"{category_router.prefix}/{randint(1, 100)}"
        )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_category_update_non_existing(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.put(
            url=f"{category_router.prefix}/{randint(1, 100)}",
            json={"name": faker.ecommerce_category()},
        )
    assert response.status_code == status.HTTP_404_NOT_FOUND
