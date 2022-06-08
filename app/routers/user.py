from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import ActiveSession
from app.models.user import User, UserCreate, UserDisplay

router = APIRouter(
    tags=[User.__tablename__.capitalize()],
    prefix=f"/{User.__tablename__}",
)


@router.get(
    path="/", status_code=status.HTTP_200_OK, response_model=List[UserDisplay]
)
async def get_all_users(
    session: Session = ActiveSession,
    offset: int = 0,
    limit: int = Query(default=50, lte=50),
) -> List[UserDisplay]:
    users = session.query(User).offset(offset).limit(limit).all()
    return [UserDisplay(**user.dict()) for user in users]


@router.get(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserDisplay,
)
async def get_user(
    session: Session = ActiveSession,
    user_id: int = Query(..., gt=0),
) -> UserDisplay:
    user: Optional[User] = (
        session.query(User).filter(User.id == user_id).first()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} does not exist.",
        )
    return UserDisplay(**user.dict())


@router.post(
    path="/", status_code=status.HTTP_201_CREATED, response_model=UserDisplay
)
async def create_user_registration(
    user_create_payload: UserCreate,
    session: Session = ActiveSession,
) -> UserDisplay:
    user: User = User(**user_create_payload.dict())
    result = session.query(User).filter(User.email == user.email).first()
    if result is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {user.email} already exists.",
        )
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserDisplay(**user.dict())


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    session: Session = ActiveSession,
    user_id: int = Query(..., gt=0),
) -> None:
    user: Optional[User] = (
        session.query(User).filter(User.id == user_id).first()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    session.delete(user)
    session.commit()
