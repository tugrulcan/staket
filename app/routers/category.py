from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db import ActiveSession
from app.models.category import Category, CategoryCreate, CategoryDisplay

router = APIRouter(
    tags=[Category.__tablename__.capitalize()],
    prefix=f"/products/{Category.__tablename__}",
)


@router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=List[CategoryDisplay],
)
async def get_all_categories(
    session: AsyncSession = ActiveSession,
    offset: int = 0,
    limit: int = Query(default=50, lte=50),
) -> List[CategoryDisplay]:
    result = await session.execute(
        select(Category).offset(offset).limit(limit)
    )
    categories: List[CategoryDisplay] = result.scalars().all()
    return categories


@router.get(
    path="/{category_id}",
    status_code=status.HTTP_200_OK,
    response_model=CategoryDisplay,
)
async def get_category(
    session: AsyncSession = ActiveSession,
    category_id: int = Query(..., gt=0),
) -> CategoryDisplay:
    result = await session.execute(
        select(Category).where(Category.id == category_id)
    )
    category: Optional[Category] = result.scalars().first()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} does not exist.",
        )
    return CategoryDisplay(**category.dict())


@router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoryDisplay,
)
async def create_category(
    category_create_payload: CategoryCreate,
    session: AsyncSession = ActiveSession,
) -> CategoryDisplay:
    result = await session.execute(
        select(Category).where(Category.name == category_create_payload.name)
    )
    existing_category: Optional[CategoryDisplay] = result.scalars().first()
    if existing_category is not None:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with name"
            f" {existing_category.name} already exists.",
        )
    new_category: Category = Category(**category_create_payload.dict())
    session.add(new_category)
    await session.commit()
    return CategoryDisplay(**new_category.dict())


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    session: AsyncSession = ActiveSession,
    category_id: int = Query(..., gt=0),
) -> None:
    result = await session.execute(
        select(Category).where(Category.id == category_id)
    )
    category: Optional[CategoryDisplay] = result.scalars().first()
    if category is None:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} does not exist.",
        )
    await session.delete(category)
    await session.commit()


@router.put(
    path="/{category_id}",
    status_code=status.HTTP_200_OK,
    response_model=CategoryDisplay,
)
async def update_category(
    category_update_payload: Category,
    category_id: int = Query(..., gt=0),
    session: AsyncSession = ActiveSession,
) -> CategoryDisplay:
    result = await session.execute(
        select(Category).where(Category.id == category_id)
    )
    category: Optional[CategoryDisplay] = result.scalars().first()
    if category is None:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} does not exist.",
        )
    category.name = category_update_payload.name
    session.add(category)
    await session.commit()
    result = await session.execute(
        select(Category).where(Category.id == category_id)
    )
    updated_category: Optional[CategoryDisplay] = result.scalars().first()
    return updated_category
