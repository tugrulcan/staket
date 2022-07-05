from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from app.models.cart import Cart, CartItem
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db import ActiveSession
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
        user: User = User(
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

    result = await session.execute(
        select(Cart).where(Cart.user_id == user.id)  # type: ignore
    )
    cart: Optional[Cart] = result.scalars().first()
    if cart is None:
        cart: Cart = Cart(
            user_id=user.id,
            cart_items=[CartItem(
                product_id=product.id,
                quantity=1,
            )],
        )
        session.add(cart)
        await session.commit()
        await session.refresh(cart)
    else:
        cart.cart_items.append(CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=1,
        ))
        session.add(cart)
        await session.commit()
        await session.refresh(cart)
    return {"status": "Item added to cart"}
