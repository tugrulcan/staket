from typing import List

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import ActiveSession
from app.models import User, UserCreate
from app.models.user import UserDisplay

router = APIRouter(
    tags=[User.__tablename__.capitalize()],
    prefix=f"/{User.__tablename__}",
)


@router.get(
    path="/", status_code=status.HTTP_200_OK, response_model=List[UserDisplay]
)
async def get_all_users(
    session: AsyncSession = ActiveSession,
    offset: int = 0,
    limit: int = Query(default=50, lte=50),
) -> List[UserDisplay]:
    result = await session.execute(select(User).offset(offset).limit(limit))
    users: List[User] = result.scalars().all()
    return [UserDisplay(**user.dict()) for user in users]


@router.get(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserDisplay,
)
async def get_user(
    session: AsyncSession = ActiveSession,
    user_id: int = Query(..., gt=0),
) -> UserDisplay:
    result = await session.execute(select(User).where(User.id == user_id))
    user: User = result.scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return UserDisplay(**user.dict())


@router.post(
    path="/", status_code=status.HTTP_201_CREATED, response_model=UserDisplay
)
async def create_user_registration(
    user_create_payload: UserCreate,
    session: AsyncSession = ActiveSession,
) -> UserDisplay:
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
    return UserDisplay(**user.dict())


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    session: AsyncSession = ActiveSession,
    user_id: int = Query(..., gt=0),
) -> None:
    result = await session.execute(select(User).where(User.id == user_id))
    user: User = result.scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    await session.delete(user)
    await session.commit()
