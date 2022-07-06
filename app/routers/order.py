from typing import List, Optional

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db import ActiveSession
from app.models.cart import Cart
from app.models.order import Order, OrderDetails, OrderDisplay
from app.models.user import User

router = APIRouter(
    tags=[Order.__tablename__.capitalize()],
    prefix=f"/{Order.__tablename__}",
)


@router.post(
    "/",
    response_model=OrderDisplay,
    status_code=status.HTTP_201_CREATED,
)
async def initiate_order_processing(
    session: AsyncSession = ActiveSession,
) -> OrderDisplay:
    user_result = await session.execute(select(User).where(User.id == 1))
    user: Optional[User] = user_result.scalar_one_or_none()
    if user is None:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist.",
        )

    cart_result = await session.execute(
        select(Cart).where(Cart.user_id == user.id)
    )
    cart: Optional[Cart] = cart_result.scalar_one_or_none()
    if cart is None:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart does not exist.",
        )

    if len(cart.cart_items) == 0:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart is empty.",
        )

    total_amount: float = 0
    for cart_item in cart.cart_items:
        total_amount += cart_item.product.price

    new_order: Order = Order(
        customer_id=user.id,
        order_amount=total_amount,
        shipping_address="123 Main St, Anytown, CA 12345",
        order_details=[
            OrderDetails(
                product_id=cart_item.product.id,
            )
            for cart_item in cart.cart_items
        ],
    )

    session.add(new_order)
    await session.commit()
    await session.refresh(new_order)

    cart.cart_items = []
    session.add(cart)
    await session.commit()
    await session.refresh(cart)

    return OrderDisplay.from_orm(new_order)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[OrderDisplay],
)
async def get_all_orders(
    session: AsyncSession = ActiveSession,
) -> List[OrderDisplay]:
    user_result = await session.execute(select(User).where(User.id == 1))
    user: Optional[User] = user_result.scalar_one_or_none()
    if user is None:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist.",
        )

    result = await session.execute(
        select(Order).where(Order.customer_id == user.id)
    )
    orders: List[Order] = result.scalars().all()
    return [OrderDisplay.from_orm(order) for order in orders]
