from datetime import datetime
from typing import List

import sqlalchemy

from sqlalchemy import Column, DateTime, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

from app.models.product import Product
from app.models.user import User


class Cart(SQLModel, table=True):  # type: ignore
    __abstract__ = False
    __tablename__ = "carts"
    id: int = Field(
        primary_key=True,
        sa_column_kwargs=dict(autoincrement=True),
    )

    user_id: int = Field(
        default=None,
        sa_column=Column(ForeignKey(User.id, ondelete="CASCADE")),
    )

    cart_items: List["CartItem"] = Relationship(
        back_populates="cart",
        sa_relationship_kwargs=dict(
            cascade="all, delete-orphan",
            uselist=True,
            lazy="selectin",
        ),
    )

    user_cart: User = Relationship(
        back_populates="cart",
        sa_relationship_kwargs=dict(
            uselist=False,
        ),
    )

    created_date: datetime = Field(
        sa_column=Column(
            name="created_date",
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
        sa_column=Column(ForeignKey("carts.id", ondelete="CASCADE")),
    )
    product_id: int = Field(
        index=True,
        sa_column=Column(ForeignKey("products.id", ondelete="CASCADE")),
    )

    cart: Cart = Relationship(
        back_populates="cart_items",
        sa_relationship_kwargs=dict(
            uselist=False,
        ),
    )

    product: Product = Relationship(
        back_populates="cart_items",
        sa_relationship_kwargs=dict(
            uselist=False,
        ),
    )

    created_date: datetime = Field(
        sa_column=Column(
            name="created_date",
            type_=DateTime(),
            server_default=sqlalchemy.sql.func.now(),
        )
    )

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class CartItemDisplay(SQLModel):
    __abstract__ = True
    id: int
    product: Product
    created_date: datetime

    class Config:
        orm_mode = True


class CartDisplay(SQLModel):
    __abstract__ = True
    id: int
    cart_items: List[CartItemDisplay]

    class Config:
        orm_mode = True
