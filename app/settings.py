from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseConfig, BaseSettings, Field, PostgresDsn, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(default="staket-api")

    POSTGRES_SERVER: str = Field(default="localhost", env="POSTGRES_SERVER")
    POSTGRES_USER: str = Field(env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(env="POSTGRES_DB")
    POSTGRES_PORT: str = Field(default=5432, env="POSTGRES_PORT")

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
            port=values.get("POSTGRES_PORT"),
        )

    class Config(BaseConfig):
        case_sensitive = True
        parent_path = Path(__file__).parent
        env_file_encoding = "utf-8"
        env_file = f"{parent_path}/../.env"


settings = Settings()
