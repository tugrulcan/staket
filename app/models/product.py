from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.category import Category


class ProductBase(SQLModel, table=False):  # type: ignore
    __abstract__ = True

    name: str = Field(default=None, max_length=50)
    quantity: int = Field(default=None)
    description: str = Field(default=None, max_length=255)
    price: float = Field(default=None)

    class Config:
        orm_mode = True


class ProductDisplay(ProductBase):
    __abstract__ = True
    id: int
    category: Optional[Category]


class ProductCreate(ProductBase):
    __abstract__ = True
    category_id: Optional[int]


class Product(ProductCreate, table=True):  # type: ignore
    __abstract__ = False
    __tablename__ = "products"
    id: int = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs=dict(autoincrement=True),
    )

    category_id: Optional[int] = Field(
        default=None, foreign_key="categories.id"
    )

    category: Optional[Category] = Relationship(
        back_populates="products",
        sa_relationship_kwargs=dict(
            uselist=False,
            lazy="selectin",
        ),
    )

    cart_items: List["CartItem"] = Relationship(  # type: ignore # noqa
        back_populates="product",
        sa_relationship_kwargs=dict(
            cascade="all, delete-orphan",
            uselist=True,
            lazy="selectin",
        ),
    )

    order_details: List["OrderDetails"] = Relationship(  # type: ignore # noqa
        back_populates="product",
        sa_relationship_kwargs=dict(
            cascade="all, delete-orphan",
            uselist=True,
        ),
    )

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
