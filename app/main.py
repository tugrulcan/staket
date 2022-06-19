from typing import List

import better_exceptions

from fastapi import FastAPI, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse, Response

from app.db import ActiveSession
from app.models import User, UserCreate

better_exceptions.MAX_LENGTH = None

description = """
Stacket API helps you do awesome stuff. 🚀
"""
app = FastAPI(
    title="Stacket API",
    description=description,
    version="0.0.1",
    terms_of_service="https://github.com/tugrulcan/staket/blob/main/LICENSE",
    contact={
        "name": "Tugrul Can Söllü",
        "url": "https://www.linkedin.com/in/tugrulcan/",
        "email": "tugrulcansollu+stacketapi@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/tugrulcan/staket/blob/main/LICENSE",
    },
    redoc_url=None,
)


@app.get("/")
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/db_ready")
async def check_db_readiness(
    session: AsyncSession = ActiveSession,
) -> Response:
    if session.is_active:
        return Response(
            status_code=status.HTTP_200_OK,
            content="Database is ready.",
        )
    else:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database is not ready.",
        )


@app.get("/users", response_model=List[User])
async def get_users(
    session: AsyncSession = ActiveSession,
    offset: int = 0,
    limit: int = Query(default=50, lte=50),
) -> List[User]:  # pragma: no cover
    result = await session.execute(select(User).offset(offset).limit(limit))
    users: List[User] = result.scalars().all()
    return users


@app.post("/users")
async def add_user(
    user_create_payload: UserCreate,
    session: AsyncSession = ActiveSession,
) -> User:  # pragma: no cover
    user = User(**user_create_payload.dict())
    result = await session.execute(
        select(User).where(User.email == user.email)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists.",
        )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
