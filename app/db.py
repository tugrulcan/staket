from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import *  # noqa
from app.settings import settings

engine = create_async_engine(
    url=settings.SQLALCHEMY_DATABASE_URI,
    echo=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncSession:
    try:
        async with SessionLocal() as session:
            yield session
    except Exception as e:
        raise e


ActiveSession = Depends(get_session)
