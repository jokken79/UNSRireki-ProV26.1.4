"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "UNS Rirekisho Pro"
    APP_VERSION: str = "26.1.4"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Company Info
    COMPANY_NAME: str = "ユニバーサル企画株式会社"
    COMPANY_NAME_EN: str = "Universal Kikaku Co., Ltd."
    COMPANY_WEBSITE: str = "https://www.uns-kikaku.com"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/uns_rirekisho"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # JWT Authentication
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3200",
        "http://127.0.0.1:3000",
    ]

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"]

    # Storage (Supabase/S3)
    STORAGE_TYPE: str = "local"  # "local", "supabase", "s3"
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    S3_BUCKET: str = ""
    S3_REGION: str = ""

    # Redis (optional caching)
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_ENABLED: bool = False

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    # Additional Trusted Hosts
    ADDITIONAL_TRUSTED_HOSTS: List[str] = []


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
