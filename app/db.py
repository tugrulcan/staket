from typing import Generator

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Connectable
from sqlalchemy.orm import Session
from sqlmodel import SQLModel

from app.settings import settings

engine = create_engine(
    url=settings.SQLALCHEMY_DATABASE_URI,
    echo=True,
)


def create_db_and_tables(bind: Connectable) -> None:
    SQLModel.metadata.create_all(bind=bind)


def get_session() -> Generator[Session, None, None]:
    with Session(bind=engine) as session:  # type: ignore
        with session.begin():
            yield session


ActiveSession = Depends(get_session)
