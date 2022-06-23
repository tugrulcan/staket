from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db import ActiveSession
from app.models.product import Product, ProductCreate, ProductDisplay

router = APIRouter(
    tags=[Product.__tablename__.capitalize()],
    prefix=f"/{Product.__tablename__}",
)


@router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=List[ProductDisplay],
)
async def get_all_products(
    session: AsyncSession = ActiveSession,
    offset: int = 0,
    limit: int = Query(default=50, lte=50),
) -> List[ProductDisplay]:
    result = await session.execute(select(Product).offset(offset).limit(limit))
    products: List[ProductDisplay] = result.scalars().all()
    return products


@router.get(
    path="/{product_id}/",
    status_code=status.HTTP_200_OK,
    response_model=ProductDisplay,
)
async def get_product(
    session: AsyncSession = ActiveSession,
    product_id: int = Query(..., gt=0),
) -> ProductDisplay:
    result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    product: Optional[ProductDisplay] = result.scalars().first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} does not exist.",
        )
    return ProductDisplay(**product.dict())


@router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductDisplay,
)
async def create_product(
    product_create_payload: ProductCreate,
    session: AsyncSession = ActiveSession,
) -> ProductDisplay:
    result = await session.execute(
        select(Product).where(Product.name == product_create_payload.name)
    )
    product_exists: Optional[ProductDisplay] = result.scalars().first()
    if product_exists is not None:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with name "
            f"{product_create_payload.name} already exists.",
        )
    new_product: Product = Product(**product_create_payload.dict())
    session.add(new_product)
    await session.commit()
    return ProductDisplay(**new_product.dict())


@router.delete(
    path="/{product_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    product_id: int,
    session: AsyncSession = ActiveSession,
) -> None:
    result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    product: Optional[ProductDisplay] = result.scalars().first()
    if product is None:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} does not exist.",
        )
    await session.delete(product)
    await session.commit()


@router.put(
    path="/{product_id}/",
    status_code=status.HTTP_200_OK,
    response_model=ProductDisplay,
)
async def update_product(
    product_update_payload: ProductCreate,
    session: AsyncSession = ActiveSession,
    product_id: int = Query(..., gt=0),
) -> ProductDisplay:
    result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    product_exists: Optional[ProductDisplay] = result.scalars().first()
    if product_exists is None:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} does not exist.",
        )

    update_data = product_update_payload.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(product_exists, key, value)

    session.add(product_exists)

    await session.commit()
    return ProductDisplay(**product_exists.dict())
