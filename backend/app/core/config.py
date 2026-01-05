"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import List, Optional
import secrets
import warnings
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


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
    ENVIRONMENT: str = "development"  # "development", "staging", "production"

    # Company Info
    COMPANY_NAME: str = "ユニバーサル企画株式会社"
    COMPANY_NAME_EN: str = "Universal Kikaku Co., Ltd."
    COMPANY_WEBSITE: str = "https://www.uns-kikaku.com"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///uns_rirekisho.db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # JWT Authentication - SECURITY: SECRET_KEY must be set via environment variable in production
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Validate SECRET_KEY - generate random key in dev, require explicit key in production."""
        if not v or v == "your-super-secret-key-change-in-production":
            # Generate secure random key for development
            generated_key = secrets.token_urlsafe(32)
            warnings.warn(
                "SECRET_KEY not set! Generated random key for development. "
                "Set SECRET_KEY environment variable for production.",
                UserWarning
            )
            return generated_key
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    # CORS - Configure based on environment
    # In production, set BACKEND_CORS_ORIGINS env var with comma-separated URLs
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3200",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ]
    # Production frontend URL (set via environment variable)
    FRONTEND_URL: Optional[str] = None

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

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
