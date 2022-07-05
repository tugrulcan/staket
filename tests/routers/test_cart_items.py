from random import randint
from typing import Optional

import faker_commerce
import pytest

from faker import Faker
from httpx import AsyncClient, Response
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.testclient import TestClient

from app.models.category import Category
from app.models.product import Product
from app.routers.cart import router as cart_router


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
    faker.add_provider(faker_commerce.Provider)

    # Insert a category
    category: Category = Category(
        name=faker.ecommerce_category(),
        products=[
            Product(
                name=faker.ecommerce_name(),
                description=faker.text(),
                price=faker.pydecimal(left_digits=4, right_digits=2, positive=True),
                quantity=0,
            )
        ],
    )
    session.add(category)
    await session.commit()

    result = await session.execute(
        select(Category).where(Category.id == category.id)
    )
    category: Optional[Category] = result.scalar_one_or_none()
    assert category is not None

    session.add(category)
    await session.commit()

    result = await session.execute(
        select(Product).where(Product.id == category.products[0].id)
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

@pytest.mark.asyncio
async def test_adding_product_into_cart(
    client: TestClient,
    session: AsyncSession,
    faker: Faker,
) -> None:
    faker.add_provider(faker_commerce.Provider)

    # Insert a category
    category: Category = Category(
        name=faker.ecommerce_category(),
        products=[
            Product(
                name=faker.ecommerce_name(),
                description=faker.text(),
                price=faker.pydecimal(left_digits=4, right_digits=2, positive=True),
                quantity=faker.random_int(min=1, max=10),
            )
        ],
    )
    session.add(category)
    await session.commit()

    result = await session.execute(
        select(Category).where(Category.id == category.id)
    )
    category: Optional[Category] = result.scalar_one_or_none()
    assert category is not None

    session.add(category)
    await session.commit()

    result = await session.execute(
        select(Product).where(Product.id == category.products[0].id)
    )
    product: Optional[Product] = result.scalars().first()
    assert product is not None, "Product was not inserted"

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.post(
            url=f"{cart_router.prefix}/add?product_id=1",
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "status": "Item added to cart",
    }

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.post(
            url=f"{cart_router.prefix}/add?product_id=1",
        )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "status": "Item added to cart",
    }

