from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SIGNAL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "local"
    log_level: str = "INFO"
    frontend_origin: str = "http://localhost:3000"
    use_fixtures: bool = True
    news_api_key: str | None = None
    fred_api_key: str | None = None
    scoring_config_path: str | None = None
    max_agent_retries: int = Field(default=2, ge=0, le=5)

    @property
    def cors_origins(self) -> list[str]:
        return [self.frontend_origin, "http://127.0.0.1:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
