from sqlmodel import Field, SQLModel


class CategoryBase(SQLModel, table=False):  # type: ignore
    __abstract__ = True

    name: str = Field(default=None, max_length=50)

    class Config:
        orm_mode = True


class CategoryDisplay(CategoryBase):
    __abstract__ = True
    id: int


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryCreate, table=True):  # type: ignore
    __abstract__ = False
    __tablename__ = "categories"
    id: int = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs=dict(autoincrement=True),
    )

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
