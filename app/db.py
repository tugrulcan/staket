from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models import *  # noqa
from app.settings import settings

engine = create_engine(
    url=settings.SQLALCHEMY_DATABASE_URI,
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=Session
)


def get_session() -> Session:
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


ActiveSession = Depends(get_session)
