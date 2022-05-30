from fastapi import Depends
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine

engine = create_engine(
    url="ASDASD",
    echo=True,
)


def create_db_and_tables(engine) -> None:
    SQLModel.metadata.create_all(bind=engine)


def get_session() -> Session:
    with Session(bind=engine) as session:
        yield session


ActiveSession = Depends(get_session)
