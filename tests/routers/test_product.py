from random import randint
from typing import List

import pytest

from faker import Faker
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.testclient import TestClient

from app.models.category import Category
from app.models.product import Product, ProductCreate, ProductDisplay
from app.routers.product import router as product_router
from tests.conftest import insert_categories, insert_products


@pytest.mark.asyncio
async def test_get_non_existing_product(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.get(
            url=f"{product_router.prefix}/{randint(1, 100)}/"
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_product(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    products: List[Product] = await insert_products(
        session=session, count=1, fake=faker
    )
    product: ProductDisplay = ProductDisplay(**products[0].dict())

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.get(
            url=f"{product_router.prefix}/{products[0].id}/"
        )

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == product.dict()


@pytest.mark.asyncio
async def test_get_all_products(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    product_count = randint(3, 82)
    products_in_db: List[Product] = await insert_products(
        session=session, count=product_count, fake=faker
    )
    products: List[ProductDisplay] = [
        ProductDisplay.from_orm(product) for product in products_in_db
    ]

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.get(
            url=f"{product_router.prefix}/?limit={product_count+1}"
        )

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == product_count

    for p in response_json:
        product_in_response: ProductDisplay = ProductDisplay(**p)
        product_in_db: ProductDisplay = next(
            product
            for product in products
            if product.id == product_in_response.id
        )

        assert (
            product_in_response == product_in_db
        ), "Product in response should be the same as in db"


@pytest.mark.asyncio
async def test_creating_product(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    categories: List[Category] = await insert_categories(
        session=session, count=1, fake=faker
    )

    product_create_payload: ProductCreate = ProductCreate(
        name=faker.name(),
        description=faker.text(),
        price=faker.pydecimal(left_digits=2, right_digits=2),
        category_id=categories[0].id,
    )
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.post(
            url=f"{product_router.prefix}/",
            json=product_create_payload.dict(),
        )

    assert response.status_code == status.HTTP_201_CREATED
    created_product: ProductDisplay = ProductDisplay(**response.json())
    assert created_product.name == product_create_payload.name
    assert created_product.description == product_create_payload.description
    assert created_product.price == product_create_payload.price


@pytest.mark.asyncio
async def test_deleting_product(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    products: List[Product] = await insert_products(
        session=session, count=1, fake=faker
    )

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.delete(
            url=f"{product_router.prefix}/{products[0].id}/"
        )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_updating_product(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    products: List[Product] = await insert_products(
        session=session, count=1, fake=faker
    )

    product_update_payload: ProductCreate = ProductCreate(
        name=faker.name(),
        description=faker.text(),
        price=faker.pydecimal(left_digits=2, right_digits=2),
    )
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.put(
            url=f"{product_router.prefix}/{products[0].id}/",
            json=product_update_payload.dict(),
        )

    assert response.status_code == status.HTTP_200_OK
    updated_product: ProductDisplay = ProductDisplay(**response.json())
    assert updated_product.name == product_update_payload.name
    assert updated_product.description == product_update_payload.description
    assert updated_product.price == product_update_payload.price
