from typing import List

from sqlmodel import Field, Relationship, SQLModel


class CategoryBase(SQLModel, table=False):  # type: ignore
    __abstract__ = True

    name: str = Field(
        default=None,
        min_length=3,
        max_length=50,
    )

    class Config:
        orm_mode = True


class CategoryDisplay(CategoryBase, table=False):  # type: ignore
    __abstract__ = True
    id: int


class CategoryCreate(CategoryBase, table=False):  # type: ignore
    pass


class Category(CategoryCreate, table=True):  # type: ignore
    __abstract__ = False
    __tablename__ = "categories"
    id: int = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs=dict(autoincrement=True),
    )

    products: List["Product"] = Relationship(  # type: ignore # noqa
        back_populates="category",
        sa_relationship_kwargs=dict(
            cascade="all, delete-orphan",
            uselist=True,
        ),
    )

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
