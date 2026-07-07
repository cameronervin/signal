from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    env: str = Field(default="local", validation_alias="SIGNAL_ENV")
    log_level: str = Field(default="INFO", validation_alias="SIGNAL_LOG_LEVEL")
    frontend_origin: str = Field(
        default="http://localhost:3000",
        validation_alias="SIGNAL_FRONTEND_ORIGIN",
    )
    news_api_key: str | None = Field(
        default=None,
        validation_alias="SIGNAL_NEWS_API_KEY",
    )
    fred_api_key: str | None = Field(
        default=None,
        validation_alias="SIGNAL_FRED_API_KEY",
    )
    census_api_key: str | None = Field(
        default=None,
        validation_alias="SIGNAL_CENSUS_API_KEY",
    )
    nominatim_email: str | None = Field(
        default=None,
        validation_alias="SIGNAL_NOMINATIM_EMAIL",
    )
    public_data_user_agent: str = Field(
        default="Signal API",
        validation_alias="SIGNAL_PUBLIC_DATA_USER_AGENT",
    )
    public_data_cache_ttl_seconds: int = Field(
        default=3600,
        ge=0,
        validation_alias="SIGNAL_PUBLIC_DATA_CACHE_TTL_SECONDS",
    )
    scoring_config_path: str | None = Field(
        default=None,
        validation_alias="SIGNAL_SCORING_CONFIG_PATH",
    )
    max_agent_retries: int = Field(
        default=2,
        ge=0,
        le=5,
        validation_alias="SIGNAL_MAX_AGENT_RETRIES",
    )
    agent_research_tools_enabled: bool = Field(
        default=True,
        validation_alias="SIGNAL_AGENT_RESEARCH_TOOLS_ENABLED",
    )
    agent_research_max_tool_rounds: int = Field(
        default=3,
        ge=0,
        le=5,
        validation_alias="SIGNAL_AGENT_RESEARCH_MAX_TOOL_ROUNDS",
    )
    postgres_user: str = Field(
        default="postgres",
        validation_alias="POSTGRES_USER",
    )
    postgres_password: str = Field(
        default="postgres",
        validation_alias="POSTGRES_PASSWORD",
    )
    postgres_db: str = Field(
        default="signal",
        validation_alias="POSTGRES_DB",
    )
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5433/signal",
        validation_alias="DATABASE_URL",
    )
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="SIGNAL_CELERY_BROKER_URL",
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/1",
        validation_alias="SIGNAL_CELERY_RESULT_BACKEND",
    )
    llm_provider: Literal["litellm"] = Field(
        default="litellm",
        validation_alias="SIGNAL_LLM_PROVIDER",
    )
    llm_model: str = Field(
        default="signal-chat",
        validation_alias="SIGNAL_LLM_MODEL",
    )
    litellm_api_base: str = Field(
        default="http://localhost:4000",
        validation_alias="SIGNAL_LITELLM_API_BASE",
    )
    litellm_api_key: str | None = Field(
        default=None,
        validation_alias="SIGNAL_LITELLM_API_KEY",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [self.frontend_origin, "http://127.0.0.1:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
