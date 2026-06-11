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

    # Database
    database_url: str = (
        "sqlite:///./arogya_mitra.db"
    )

    # JWT / Security
    jwt_secret_key: str = ""
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
        "http://localhost:3000"
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
    def cors_origins_list(
        self
    ) -> List[str]:

        return [
            origin.strip()
            for origin in
            self.cors_origins.split(",")
        ]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith(
            "sqlite"
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()