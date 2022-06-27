from random import randint
from typing import Optional

import pytest

from faker import Faker
from httpx import AsyncClient, Response
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.testclient import TestClient

from app.routers.cart import router as cart_router
from app.models.product import Product
from app.models.category import Category


@pytest.mark.asyncio
async def test_adding_non_existing_product_into_cart(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.post(
            url=f"{cart_router.prefix}/add?product_id=1",
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Product with id 1 does not exist.",
    }


@pytest.mark.asyncio
async def test_adding_non_stock_product_into_cart(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    # Insert a category
    result = await session.execute(
        insert(Category).values(
            Category(
                name="Test Category",
            )
        )
    )
    category: Optional[Category] = result.scalars().first()
    assert category is not None

    result = await session.execute(
        insert(Product).values(
            Product(
                id=1,
                name=faker.name(),
                price=randint(1, 100)/0.32,
                quantity=0,
                category_id=category.id,
            )
        )
    )
    product: Optional[Product] = result.scalars().first()
    assert product is not None, "Product was not inserted"


    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.post(
            url=f"{cart_router.prefix}/add?product_id=1",
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Product with id 1 is out of stock.",
    }