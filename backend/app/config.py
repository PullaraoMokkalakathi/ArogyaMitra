from functools import lru_cache
from typing import List
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "ArogyaMitra"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    port: int = 8000
    host: str = "0.0.0.0"

    # Database
    database_url: str = (
        "sqlite:///./arogya_mitra.db"
    )

    # Database Connection Pool (PostgreSQL)
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_recycle: int = 300
    db_pool_timeout: int = 30

    # JWT / Security
    jwt_secret_key: str = "arogya-mitra-insecure-dev-secret-key-change-in-production-12345"
    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # AI Models
    groq_api_key: str = ""
    groq_model: str = (
        "llama-3.3-70b-versatile"
    )

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # CORS
    cors_origins: str = (
        "http://localhost:5173,"
        "http://localhost:3000,"
        "http://127.0.0.1:5173,"
        "http://127.0.0.1:3000"
    )

    # Rate Limiting
    rate_limit_general: str = (
        "100/minute"
    )

    rate_limit_auth: str = (
        "20/minute"
    )

    rate_limit_ai: str = (
        "10/minute"
    )

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.cors_origins:
            return ["http://localhost:5173", "http://localhost:3000"] if not self.is_production else []

        raw = self.cors_origins.strip()
        # Handle bracketed strings like [http://localhost:5173, https://your-frontend.vercel.app]
        if raw.startswith("[") and raw.endswith("]"):
            raw = raw[1:-1]

        origins = []
        for item in raw.split(","):
            cleaned = item.strip().strip("'\"").rstrip("/")
            if cleaned:
                origins.append(cleaned)

        # In production, avoid wildcard origins for safety with credentials
        if self.is_production:
            origins = [o for o in origins if o != "*"]

        return origins

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
