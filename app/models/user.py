from typing import List

from pydantic import EmailStr, validator
from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel

from helpers import hash_password, is_hash, verify_password


class UserBase(SQLModel):
    __abstract__ = True

    name: str = Field(default=None, max_length=50)
    email: EmailStr = Field(
        sa_column=Column(String(100), unique=True, nullable=False)
    )
    is_active: bool = Field(default=True)

    class Config:
        orm_mode = True


class UserDisplay(UserBase):
    __abstract__ = True
    id: int


class UserCreate(UserBase):
    password: str = Field(sa_column=Column(String(255), nullable=False))

    class Config:
        orm_mode = True


class User(UserCreate, table=True):  # type: ignore
    __abstract__ = False
    __tablename__ = "users"
    id: int = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs=dict(autoincrement=True),
    )

    cart: "Cart" = Relationship(  # type: ignore # noqa
        back_populates="user_cart",
        sa_relationship_kwargs=dict(
            uselist=False,
        ),
    )

    orders: List["Order"] = Relationship(  # type: ignore # noqa
        back_populates="user_info",
        sa_relationship_kwargs=dict(
            uselist=True,
            lazy="selectin",
        ),
    )

    @validator("password", pre=True)
    def hash_password(cls, pw: str) -> str:  # pragma: no cover
        if is_hash(pw):
            return pw
        return hash_password(pw)

    def check_password(self, password: str) -> bool:  # pragma: no cover
        return verify_password(self.password, password)

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
