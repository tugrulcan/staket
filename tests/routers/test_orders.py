from random import randint
from typing import List

import faker_commerce
import pytest

from faker import Faker
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.testclient import TestClient

from app.constants import OrderStatus
from app.models.category import Category
from app.models.order import OrderDisplay
from app.models.product import Product
from app.routers.cart import router as cart_router
from app.routers.order import router as order_router


@pytest.mark.asyncio
async def test_initiate_order_processing(
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
                price=faker.pydecimal(
                    left_digits=4, right_digits=2, positive=True
                ),
                quantity=faker.random_int(min=1, max=10),
            )
        ],
    )
    session.add(category)
    await session.commit()
    await session.refresh(category)
    for _ in range(randint(1, 10)):
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response: Response = await ac.post(
                url=f"{cart_router.prefix}/add?product_id=1",
            )
        assert response.status_code == status.HTTP_201_CREATED

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.get(  # type: ignore
            url=f"{cart_router.prefix}/",
        )

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.post(  # type: ignore
            url=f"{order_router.prefix}/",
        )

    assert response.status_code == status.HTTP_201_CREATED

    created_order: OrderDisplay = OrderDisplay(**response.json())
    assert created_order.id is not None
    assert created_order.customer_id == 1
    assert created_order.status == OrderStatus.PENDING
    assert created_order.shipping_address is not None
    assert created_order.order_date is not None
    assert created_order.order_amount > 0


@pytest.mark.asyncio
async def test_get_all_orders(
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
                price=faker.pydecimal(
                    left_digits=4, right_digits=2, positive=True
                ),
                quantity=faker.random_int(min=1, max=10),
            )
        ],
    )
    session.add(category)
    await session.commit()
    await session.refresh(category)
    for _ in range(randint(1, 10)):
        async with AsyncClient(app=client.app, base_url="http://test") as ac:
            response: Response = await ac.post(
                url=f"{cart_router.prefix}/add?product_id=1",
            )
        assert response.status_code == status.HTTP_201_CREATED

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.get(  # type: ignore
            url=f"{cart_router.prefix}/",
        )

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.post(  # type: ignore
            url=f"{order_router.prefix}/",
        )

    assert response.status_code == status.HTTP_201_CREATED

    async with AsyncClient(app=client.app, base_url="http://test") as ac:
        response: Response = await ac.get(  # type: ignore
            url=f"{order_router.prefix}/",
        )

    assert response.status_code == status.HTTP_200_OK
    orders: List[OrderDisplay] = [
        OrderDisplay(**order) for order in response.json()
    ]
    assert len(orders) == 1
