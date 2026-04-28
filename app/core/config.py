"""Pydantic Settings — single source of truth for env-driven config."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    app_log_level: str = "INFO"
    app_max_critic_loops: int = 2

    openai_api_key: str = ""
    anthropic_api_key: str = ""

    database_url: str = "postgresql+psycopg://app:app@localhost:5432/finai"

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"


settings = Settings()
