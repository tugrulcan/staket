from typing import AsyncGenerator, Generator

import pytest

from fastapi.testclient import TestClient
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
from app.models import *  # noqa
from app.settings import settings

# Source: https://gist.github.com/kampikd/513f67b0aa757da766b8ad3c795281ee#file-pytest_transactions_full-py  # noqa


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
    from app.main import app

    app.dependency_overrides[db.get_session] = lambda: session

    with TestClient(app) as client:
        try:
            yield client
        finally:
            pass
