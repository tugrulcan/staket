from datetime import datetime
from typing import List

import sqlalchemy

from app.models.user import User
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.sql.functions import now
from sqlmodel import Field, SQLModel, Relationship


class Cart(SQLModel, table=True):  # type: ignore
    __abstract__ = False
    __tablename__ = "cart"
    id: int = Field(
        primary_key=True,
        sa_column_kwargs=dict(autoincrement=True),
    )

    user_id: int = Field(
        default=None,
        sa_column=Column(ForeignKey(User.id, ondelete="CASCADE")),
    )

    cart_items: List["CartItem"] = Relationship(  # type: ignore # noqa
        back_populates="cart",
        sa_relationship_kwargs=dict(
            cascade="all, delete-orphan",
            uselist=True,
        ),
    )

    user_cart: User = Relationship(  # type: ignore # noqa
        back_populates="carts",
        sa_relationship_kwargs=dict(
            uselist=False,
        ),
    )

    created_date: datetime = Field(
        sa_column=Column(
            name='created_date',
            type_=DateTime(),
            server_default=sqlalchemy.sql.func.now(),
        )

    )
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class CartItem(SQLModel, table=True):  # type: ignore
    __abstract__ = False
    __tablename__ = "cart_items"

    id: int = Field(
        primary_key=True,
        sa_column_kwargs=dict(autoincrement=True),
    )
    cart_id: int = Field(
        index=True,
        sa_column=Column(ForeignKey(Cart.id, ondelete="CASCADE")),
    )
    product_id: int = Field(
        index=True,
        sa_column=Column(ForeignKey("products.id", ondelete="CASCADE")),
    )

    cart: Cart = Relationship(  # type: ignore # noqa
        back_populates="cart_items",
        sa_relationship_kwargs=dict(
            uselist=False,
        ),
    )

    product: "Product" = Relationship(  # type: ignore # noqa
        back_populates="cart_items",
        sa_relationship_kwargs=dict(
            uselist=False,
        ),
    )

    created_date: datetime = Field(
        sa_column=Column(
            name='created_date',
            type_=DateTime(),
            server_default=sqlalchemy.sql.func.now(),
        )

    )

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
