"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Personalized Travel Planner", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")

    database_url: str = Field(alias="DATABASE_URL")

    secret_key: str = Field(alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    pdf_output_dir: str = Field(default="generated_pdfs", alias="PDF_OUTPUT_DIR")
    allowed_origins: list[str] | str = Field(default_factory=list, alias="ALLOWED_ORIGINS")

    @field_validator("app_env")
    @classmethod
    def _normalize_env(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"development", "testing", "production"}:
            raise ValueError("APP_ENV must be development, testing, or production")
        return normalized

    @field_validator("database_url")
    @classmethod
    def _validate_database_url(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("DATABASE_URL is required")
        if not normalized.startswith("mssql+pyodbc://"):
            raise ValueError("DATABASE_URL must use SQL Server with mssql+pyodbc")
        if "TravelPlanner" not in normalized:
            raise ValueError("DATABASE_URL must use the TravelPlanner database")
        return normalized

    @field_validator("secret_key")
    @classmethod
    def _validate_secret_key(cls, value: str) -> str:
        if len(value.strip()) < 32:
            raise ValueError("SECRET_KEY must contain at least 32 characters")
        return value.strip()

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [item.strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        raise TypeError("ALLOWED_ORIGINS must be a CSV string or list")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
