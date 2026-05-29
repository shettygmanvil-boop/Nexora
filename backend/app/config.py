"""
Maproom — Integrated Application Configuration
=============================================
Centralised settings using pydantic-settings.
Exposes both lowercase/uppercase configurations and initialises
the shared Gemini LLM wrapper for CrewAI.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import LLM

# Resolve paths for environmental files
ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_ENV = ROOT_DIR / "backend" / ".env"
ROOT_ENV = ROOT_DIR / ".env"

from dotenv import load_dotenv
load_dotenv(dotenv_path=BACKEND_ENV, override=True)
load_dotenv(dotenv_path=ROOT_ENV, override=True)


class Settings(BaseSettings):
    """
    Application-wide settings.
    Supports keys from all three branches: Manvil, pratyush, and smaran.
    """

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_ENV), str(ROOT_ENV)),
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

    # ── Gemini / LLM ──────────────────────────────────────────────────────
    gemini_api_key: str = Field(default="", description="Gemini API key")

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

    # ── Uppercase properties for backward compatibility with pratyush branch ────
    @property
    def HOST(self) -> str:
        return self.host

    @property
    def PORT(self) -> int:
        return self.port

    @property
    def LLM_PROVIDER(self) -> str:
        if self.gemini_api_key:
            return "gemini"
        elif self.openai_api_key:
            return "openai"
        return "mock"

    @property
    def LLM_MODEL_NAME(self) -> str:
        if self.LLM_PROVIDER == "gemini":
            return "gemini-2.5-flash"
        return self.openai_model

    @property
    def OPENAI_API_KEY(self) -> str:
        return self.openai_api_key

    @property
    def GEMINI_API_KEY(self) -> str:
        return self.gemini_api_key

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
    """
    return Settings()


# Convenience alias — import this in modules that need settings
settings = get_settings()

# ── Shared LLM Wrapper for CrewAI ─────────────────────────────────────────────
# Set up Gemini model using langchain
langchain_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=settings.gemini_api_key or "mock_key",
)

shared_llm = LLM(
    model="gemini/gemini-2.5-flash",
    custom_llm=langchain_gemini
)
