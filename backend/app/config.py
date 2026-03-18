from pydantic import model_validator
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://buildwise:buildwise@localhost:5432/buildwise"

    @model_validator(mode="after")
    def fix_database_url(self) -> "Settings":
        """Convert postgresql:// to postgresql+asyncpg:// for async SQLAlchemy."""
        if self.DATABASE_URL.startswith("postgresql://"):
            self.DATABASE_URL = self.DATABASE_URL.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        return self

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "CHANGE_ME_TO_RANDOM_STRING"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Email
    RESEND_API_KEY: str = "re_CHANGE_ME"

    # Prototype
    DEFAULT_PROTOTYPE: Literal["P1", "P2", "P3"] = "P1"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
