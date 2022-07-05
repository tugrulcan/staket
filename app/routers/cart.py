from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db import ActiveSession
from app.models.cart import Cart, CartDisplay, CartItem
from app.models.product import Product
from app.models.user import User

router = APIRouter(
    tags=[Cart.__tablename__.capitalize()],
    prefix=f"/{Cart.__tablename__}",
)


@router.post(
    "/add",
    status_code=status.HTTP_201_CREATED,
)
async def add_to_cart(
    product_id: int = Query(..., gt=0),
    session: AsyncSession = ActiveSession,
) -> dict[str, str]:
    result = await session.execute(
        select(Product).where(Product.id == product_id)
    )
    product: Optional[Product] = result.scalars().first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} does not exist.",
        )
    if product.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} is out of stock.",
        )

    demo_user = await session.execute(select(User).where(User.id == 1))
    user: Optional[User] = demo_user.scalars().first()
    if user is None:
        user: User = User(  # type: ignore
            id=1,
            name="Demo User",
            email="demo@demo.com",
            is_active=True,
            password="demo",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        assert user is not None

    result = await session.execute(select(Cart).where(Cart.user_id == user.id))
    cart: Optional[Cart] = result.scalars().first()
    if cart is None:
        cart: Cart = Cart(  # type: ignore
            user_id=user.id,
            cart_items=[
                CartItem(
                    product_id=product.id,
                    quantity=1,
                )
            ],
        )
        session.add(cart)
        await session.commit()
        await session.refresh(cart)
    else:
        cart.cart_items.append(
            CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=1,
            )
        )
        session.add(cart)
        await session.commit()
        await session.refresh(cart)
    return {"status": "Item added to cart"}


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CartDisplay,
)
async def get_all_cart_items(
    session: AsyncSession = ActiveSession,
) -> CartDisplay:
    demo_user = await session.execute(select(User).where(User.id == 1))
    user: Optional[User] = demo_user.scalars().first()
    if user is None:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist.",
        )

    result = await session.execute(select(Cart).where(Cart.user_id == user.id))
    cart: Optional[Cart] = result.scalar_one_or_none()
    return CartDisplay.from_orm(cart)


@router.delete(
    "/{cart_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_cart_item_by_id(
    cart_item_id: int = Query(..., gt=0),
    session: AsyncSession = ActiveSession,
) -> None:
    demo_user = await session.execute(select(User).where(User.id == 1))
    user: Optional[User] = demo_user.scalars().first()
    if user is None:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist.",
        )

    result = await session.execute(select(Cart).where(Cart.user_id == user.id))
    cart: Optional[Cart] = result.scalar_one_or_none()
    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart does not exist.",
        )
    cart_item: Optional[CartItem] = next(
        (
            cart_item
            for cart_item in cart.cart_items
            if cart_item.id == cart_item_id
        ),
        None,
    )
    if cart_item is None:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item with id {cart_item_id} "
            f"does not exist in cart id {cart.id}.",
        )

    cart.cart_items.remove(cart_item)
    session.add(cart)
    await session.commit()
    await session.refresh(cart)
