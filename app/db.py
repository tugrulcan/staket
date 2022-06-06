from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.models import *  # noqa
from app.settings import settings

engine = create_async_engine(
    url=settings.SQLALCHEMY_DATABASE_URI,
    echo=True,
    future=True,
)


async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


ActiveSession = Depends(get_session)
