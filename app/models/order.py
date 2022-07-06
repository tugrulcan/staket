from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.sql.functions import now
from sqlmodel import Field, Relationship, SQLModel

from app.constants import OrderStatus
from app.models.product import ProductDisplay
from app.models.user import User, UserDisplay


class Order(SQLModel, table=True):  # type: ignore
    __abstract__ = False
    __tablename__ = "orders"

    id: int = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs=dict(autoincrement=True),
    )

    order_date: datetime = Field(default=datetime.now())

    order_amount: float = Field(default=0.0)

    status: OrderStatus = Field(default=OrderStatus.PENDING)

    shipping_address: str = Field(
        default=None,
        min_length=3,
        max_length=50,
    )

    customer_id: int = Field(
        sa_column=Column(ForeignKey(User.id, ondelete="CASCADE")),
        nullable=False,
    )

    user_info: User = Relationship(
        back_populates="orders",
        sa_relationship_kwargs=dict(
            uselist=False,
            lazy="selectin",
        ),
    )

    order_details: List["OrderDetails"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs=dict(
            uselist=True,
            lazy="selectin",
        ),
    )


class OrderDetails(SQLModel, table=True):  # type: ignore
    __abstract__ = False
    __tablename__ = "order_details"

    id: int = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs=dict(autoincrement=True),
    )

    order_id: int = Field(
        sa_column=Column(ForeignKey("orders.id", ondelete="CASCADE")),
        nullable=False,
    )

    order: Order = Relationship(
        back_populates="order_details",
        sa_relationship_kwargs=dict(
            uselist=False,
            lazy="selectin",
        ),
    )

    product_id: int = Field(
        sa_column=Column(ForeignKey("products.id", ondelete="CASCADE")),
        nullable=False,
    )

    product: "Product" = Relationship(  # type: ignore # noqa
        back_populates="order_details",
        sa_relationship_kwargs=dict(
            uselist=False,
            lazy="selectin",
        ),
    )

    quantity: int = Field(
        default=1,
    )

    created_date: datetime = Field(
        sa_column=Column(
            name="created_date",
            type_=DateTime(),
            server_default=now(),
        )
    )


class OrderDetailDisplay(SQLModel, table=False):  # type: ignore
    __abstract__ = True
    id: int
    order_id: int
    product_id: int
    quantity: int
    created_date: datetime
    # order: "OrderDisplay"
    product: ProductDisplay


class OrderDisplay(SQLModel, table=False):  # type: ignore
    __abstract__ = True
    id: int
    order_date: datetime
    order_amount: float
    status: OrderStatus
    shipping_address: str
    customer_id: int
    order_details: List[OrderDetailDisplay]
    user_info: UserDisplay
