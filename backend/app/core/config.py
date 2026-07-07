from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SIGNAL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    env: str = "local"
    log_level: str = "INFO"
    frontend_origin: str = "http://localhost:3000"
    use_fixtures: bool = True
    news_api_key: str | None = None
    fred_api_key: str | None = None
    census_api_key: str | None = None
    nominatim_email: str | None = None
    public_data_user_agent: str = "Signal API local demo"
    public_data_cache_ttl_seconds: int = Field(default=3600, ge=0)
    scoring_config_path: str | None = None
    max_agent_retries: int = Field(default=2, ge=0, le=5)
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
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    llm_provider: Literal["litellm"] = "litellm"
    llm_model: str = "signal-chat"
    litellm_api_base: str = "http://localhost:4000"
    litellm_api_key: str | None = None

    @property
    def cors_origins(self) -> list[str]:
        return [self.frontend_origin, "http://127.0.0.1:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
