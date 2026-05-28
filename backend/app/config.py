"""
Maproom — Application Configuration
=====================================
Centralised settings using pydantic-settings.
All values are loaded from environment variables / .env file.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application-wide settings.
    Add new configuration keys here — never scatter os.getenv() calls
    across the codebase.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────
    app_name: str = Field(default="Maproom", description="Human-readable app name")
    app_version: str = Field(default="1.0.0")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development"
    )
    debug: bool = Field(default=False)
    secret_key: str = Field(default="change-me-in-production")

    # ── Server ─────────────────────────────────────────────────────────────
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # ── OpenAI / LLM ──────────────────────────────────────────────────────
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="LLM model for CrewAI agents")

    # ── OpenWeatherMap ─────────────────────────────────────────────────────
    openweather_api_key: str = Field(default="", description="OpenWeatherMap API key")
    openweather_base_url: str = Field(
        default="https://api.openweathermap.org/data/2.5"
    )

    # ── Air Quality (AQICN) ────────────────────────────────────────────────
    aqicn_api_key: str = Field(default="", description="AQICN air quality API key")
    aqicn_base_url: str = Field(default="https://api.waqi.info")

    # ── Database ───────────────────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/maproom"
    )

    # ── Redis ──────────────────────────────────────────────────────────────
    redis_url: str = Field(default="redis://localhost:6379/0")
    cache_ttl_seconds: int = Field(default=1800, description="Cache TTL in seconds")

    # ── Logging ────────────────────────────────────────────────────────────
    log_level: str = Field(default="INFO")

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached singleton of Settings.
    Use this everywhere instead of instantiating Settings() directly.
    """
    return Settings()


# Convenience alias — import this in modules that need settings
settings = get_settings()
