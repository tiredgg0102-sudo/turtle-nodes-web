"""Application configuration.

All configuration is environment-driven. No credentials, API keys, prices,
URLs, or infrastructure identifiers are hardcoded in source code.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # hosting-platform/


class Settings(BaseSettings):
    # ------------------------------------------------------------------ App
    APP_NAME: str = "Hosting Platform"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="development", description="development|staging|production")
    APP_DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # ------------------------------------------------------------------ Security
    SECRET_KEY: str = Field(..., description="JWT signing secret")
    ENCRYPTION_KEY: str = Field(..., description="Fernet key for at-rest credential encryption")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ------------------------------------------------------------------ Database
    DATABASE_URL: str = Field(
        default="sqlite:///./hosting.db",
        description="SQLAlchemy database URL",
    )

    # ------------------------------------------------------------------ Frontend / CORS
    FRONTEND_URL: str = "http://localhost:8000"
    CORS_ORIGINS: Any = ["http://localhost:8000", "http://127.0.0.1:8000"]

    # ------------------------------------------------------------------ Cookies
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    COOKIE_DOMAIN: Optional[str] = None

    # ------------------------------------------------------------------ Rate limiting
    RATE_LIMIT_LOGIN: int = 10          # requests per window
    RATE_LIMIT_REGISTER: int = 5
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ------------------------------------------------------------------ Email (optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: str = "Hosting Platform"
    EMAIL_VERIFICATION_REQUIRED: bool = False

    # ------------------------------------------------------------------ Discord
    DISCORD_BOT_TOKEN: Optional[str] = None
    BOT_API_KEY: Optional[str] = None
    DISCORD_GUILD_ID: Optional[str] = None
    DISCORD_STAFF_ROLE_IDS: Any = []
    DISCORD_ORDER_CHANNEL_ID: Optional[str] = None
    DISCORD_STAFF_CHANNEL_ID: Optional[str] = None
    DISCORD_NOTIFICATIONS_CHANNEL_ID: Optional[str] = None
    DISCORD_INVITE_URL: Optional[str] = None
    DISCORD_REDIRECT_BASE_URL: Optional[str] = None

    # ------------------------------------------------------------------ Pterodactyl
    PTERODACTYL_URL: Optional[str] = None
    PTERODACTYL_APP_API_KEY: Optional[str] = None
    PTERODACTYL_API_TIMEOUT: int = 30
    PTERODACTYL_DEFAULT_NODE_ID: Optional[int] = None
    PTERODACTYL_DEFAULT_LOCATION_ID: Optional[int] = None
    PTERODACTYL_DEFAULT_NEST_ID: Optional[int] = None
    PTERODACTYL_DEFAULT_EGG_ID: Optional[int] = None
    PTERODACTYL_DEFAULT_RAM: int = 1024
    PTERODACTYL_DEFAULT_CPU: int = 100
    PTERODACTYL_DEFAULT_STORAGE: int = 20480  # MB
    PTERODACTYL_DEFAULT_DISK: int = 20480
    PTERODACTYL_DEFAULT_IO: int = 500
    PTERODACTYL_DEFAULT_OVERLIMIT: bool = False

    # ------------------------------------------------------------------ Provisioning
    PROVISIONING_MAX_ATTEMPTS: int = 5
    PROVISIONING_RETRY_BACKOFF_SECONDS: int = 30

    # ------------------------------------------------------------------ Security
    BCRYPT_ROUNDS: int = 12
    SESSION_MAX_AGE_SECONDS: int = 60 * 60 * 24 * 7

    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"), env_file_encoding="utf-8", case_sensitive=True, extra="ignore")

    @validator("CORS_ORIGINS", pre=True)
    def _parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    @validator("DISCORD_STAFF_ROLE_IDS", pre=True)
    def _parse_discord_roles(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    @validator(
        "PTERODACTYL_DEFAULT_NODE_ID",
        "PTERODACTYL_DEFAULT_LOCATION_ID",
        "PTERODACTYL_DEFAULT_NEST_ID",
        "PTERODACTYL_DEFAULT_EGG_ID",
        pre=True,
    )
    def _parse_optional_int(cls, v):
        if v is None or v == "":
            return None
        return v


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
