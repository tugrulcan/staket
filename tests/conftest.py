from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.db import engine

# SQLModel.metadata.drop_all(bind=engine)
# SQLModel.metadata.create_all(bind=engine)


# def override_get_db():
#     try:
#         db = TestingSessionLocal()
#         yield db
#     finally:
#         db.close()


async def override_get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        async with session.begin() as transaction:
            session.begin_nested()
            yield session
        transaction.rollback()


# app.dependency_overrides[get_db] = override_get_db


# @pytest.fixture(autouse=True)
# def create_dummy_user(tmpdir):
#     """Fixture to execute asserts before and after a test is run"""
#     # Setup: fill with any logic you want
#     from conf_test_db import override_get_db
#
#     database = next(override_get_db())
#     new_user = User(name="John", email="john@gmail.com", password="john123")
#     database.add(new_user)
#     database.commit()
#
#     yield  # this is where the testing happens
#
#     # Teardown : fill with any logic you want
#     database.query(User).filter(User.email == "john@gmail.com").delete()
#     database.commit()
