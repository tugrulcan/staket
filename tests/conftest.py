from typing import AsyncGenerator, Generator, List

import faker_commerce
import pytest

from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel

from app import db
from app.main import app
from app.models.category import Category, CategoryCreate

# Source: https://gist.github.com/kampikd/513f67b0aa757da766b8ad3c795281ee#file-pytest_transactions_full-py  # noqa
from app.models.product import Product,ProductCreate
from app.models.user import User, UserCreate
from app.settings import settings


@pytest.fixture()
async def connection() -> AsyncGenerator[AsyncConnection, None]:
    engine: AsyncEngine = create_async_engine(
        url=settings.SQLALCHEMY_DATABASE_URI,  # TODO: Replace it with TEST_DB_URL  # noqa
        echo=True,
        future=True,
    )

    async with engine.connect() as conn:
        yield conn


@pytest.fixture()
async def setup_database(connection: AsyncConnection) -> None:

    await connection.run_sync(SQLModel.metadata.create_all)


@pytest.fixture
async def session(
    setup_database: None, connection: Engine
) -> AsyncGenerator[Session, None]:
    """Override the get_session function to return a scoped session."""
    transaction = connection.begin()
    session_local = sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with session_local() as session:
        session.begin_nested()
        yield session
        await session.rollback()
    transaction.rollback()


@pytest.fixture()
def client(session: Session) -> Generator[TestClient, None, None]:

    app.dependency_overrides[db.get_session] = lambda: session

    with TestClient(app) as client:
        try:
            yield client
        finally:
            pass


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
    users = result.scalars().all()

    assert len(users) == count, (
        "Number of users should match with the "
        "number of users inserted into the "
        "database "
    )

    return users


@pytest.mark.asyncio
async def insert_categories(
    session: AsyncSession,
    count: int = 10,
    fake: Faker = Faker(),
) -> List[Category]:
    fake.add_provider(faker_commerce.Provider)
    category_create_payloads: List[CategoryCreate] = [
        CategoryCreate(
            name=fake.ecommerce_category(),
        )
        for _ in range(count)
    ]
    result = await session.execute(select(Category))
    categories: List[Category] = result.scalars().all()
    assert len(categories) == 0, "No categories should be present"

    # Insert categories in category_create_payloads list
    for category_create_payload in category_create_payloads:
        await session.execute(
            Category.__table__.insert().values(
                **category_create_payload.dict()
            )
        )
    result = await session.execute(select(Category))
    await session.commit()
    categories = result.scalars().all()

    assert len(categories) == count, (
        "Number of categories should match with the "
        "number of categories inserted into the "
        "database "
    )

    return categories


@pytest.mark.asyncio
async def insert_products(
    session: AsyncSession,
    count: int = 10,
    fake: Faker = Faker(),
) -> List[Product]:
    fake.add_provider(faker_commerce.Provider)
    categories: List[Category] = await insert_categories(
        session=session, count=count, fake=fake
    )

    product_create_payloads: List[ProductCreate] = [
        ProductCreate(
            name=fake.ecommerce_name(),
            description=fake.text(),
            quantity=fake.pyint(),
            price=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            category_id=categories[0].id,
        )
        for i in range(count)
    ]

    result = await session.execute(select(Product))
    products: List[Product] = result.scalars().all()
    assert len(products) == 0, "No products should be present"

    # Insert products in product_create_payloads list
    for product_create_payload in product_create_payloads:
        await session.execute(
            Product.__table__.insert().values(**product_create_payload.dict())
        )
    result = await session.execute(select(Product))
    await session.commit()
    products = result.scalars().all()

    assert len(products) == count, (
        "Number of products should match with the "
        "number of products inserted into the "
        "database "
    )

    return products
