from typing import Generator

import pytest

from db import get_session
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlmodel import SQLModel

from app.models import *  # noqa
from app.settings import settings

# Source: https://gist.github.com/kampikd/513f67b0aa757da766b8ad3c795281ee#file-pytest_transactions_full-py


@pytest.fixture(scope="session")
def connection() -> Generator[Engine, None, None]:
    engine = create_engine(
        url=settings.SQLALCHEMY_DATABASE_URI,  # TODO: Replace it with TEST_DB_URL
        echo=True,
    )
    connection = engine.connect()
    try:
        yield engine
    finally:
        pass
    connection.close()


@pytest.fixture(scope="session")
def setup_database(connection):
    SQLModel.metadata.bind = connection
    SQLModel.metadata.create_all()

    # seed_database()
    try:
        yield
    finally:
        SQLModel.metadata.bind.dispose()


@pytest.fixture
def session(
    setup_database: None, connection: Engine
) -> Generator[Session, None, None]:
    """Override the get_session function to return a scoped session."""
    transaction = connection.begin()
    session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=connection)
    )
    try:
        session.begin_nested()
        yield session
        transaction.rollback()
    finally:
        session.rollback()
        session.close()


@pytest.fixture()
def client():
    from app.main import app

    app.dependency_overrides[get_session] = session

    with TestClient(app) as client:
        try:
            yield client
        finally:
            pass


# Create a fixture called session to use the session in the tests.
# This fixture is used in the tests.
# @pytest.fixture()
# def test_session() -> Session:
#     from conf_test_db import override_get_session, connection, setup_database
#     return next(override_get_session(setup_database=setup_database, connection=connection))

# @pytest.fixture(autouse=True)
# async def setup_tests():
#     """Fixture to execute asserts before and after a test is run"""
#
#     from conf_test_db import create_db_and_tables, override_get_db
#
#     # await create_db_and_tables()
#     yield  # this is where the testing happens
#
#     # Teardown : fill with any logic you want
#     # database.query(User).filter(User.email == 'john@gmail.com').delete()
#     # database.commit()
