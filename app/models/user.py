from pydantic import EmailStr, validator
from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel

from helpers import hash_password, is_hash, verify_password


class UserBase(SQLModel):
    name: str = Field(default=None, max_length=50)
    email: EmailStr = Field(
        sa_column=Column(String(100), unique=True, nullable=False)
    )
    password: str = Field(sa_column=Column(String(255), nullable=False))
    is_active: bool = Field(default=True)


class User(UserBase, table=True, table_name="users"):  # type: ignore
    id: int = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs=dict(autoincrement=True),
    )

    @validator("password", pre=True)
    def hash_password(cls, pw: str) -> str:  # pragma: no cover
        if is_hash(pw):
            return pw
        return hash_password(pw)

    def check_password(self, password: str) -> bool:  # pragma: no cover
        return verify_password(self.password, password)


class UserCreate(UserBase):
    pass
