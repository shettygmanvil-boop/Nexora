import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables and .env file.
    """
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server settings
    HOST: str = Field(default="127.0.0.1")
    PORT: int = Field(default=8000)

    # LLM provider configuration
    # Can be 'openai', 'gemini', or 'mock'
    LLM_PROVIDER: str = Field(default="mock")

    # API Keys
    OPENAI_API_KEY: str = Field(default="")
    GEMINI_API_KEY: str = Field(default="")

    # Model configuration
    LLM_MODEL_NAME: str = Field(default="gemini/gemini-1.5-flash")

# Global configurations instance
settings = Settings()
