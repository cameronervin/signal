from functools import lru_cache
from typing import Annotated

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SIGNAL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "local"
    log_level: str = "INFO"
    api_base_url: str = "http://127.0.0.1:8000"
    frontend_origin: str = "http://localhost:3000"
    extra_cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://127.0.0.1:3000"]
    )
    use_fixtures: bool = True
    news_api_key: SecretStr | None = None
    fred_api_key: SecretStr | None = None
    openai_api_key: SecretStr | None = None
    litellm_gateway_url: str | None = None
    litellm_gateway_key: SecretStr | None = None
    llm_model: str | None = None
    scoring_config_path: str = "app/agents/scoring.py"
    max_agent_retries: int = Field(default=2, ge=0, le=5)
    provider_retry_count: int = Field(default=2, ge=0, le=5)
    provider_timeout_seconds: float = Field(default=8.0, gt=0, le=60)
    request_timeout_seconds: float = Field(default=15.0, gt=0, le=120)

    @property
    def cors_origins(self) -> list[str]:
        origins = [self.frontend_origin, *self.extra_cors_origins]
        return list(dict.fromkeys(origins))

    @property
    def has_llm_key(self) -> bool:
        return self.openai_api_key is not None or self.litellm_gateway_key is not None

    @field_validator("extra_cors_origins", mode="before")
    @classmethod
    def split_extra_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("api_base_url", "frontend_origin", "litellm_gateway_url")
    @classmethod
    def validate_origin_value(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if value == "*" or not value.startswith(("http://", "https://")):
            raise ValueError("origin values must be explicit http(s) URLs")
        return value

    @field_validator("extra_cors_origins")
    @classmethod
    def validate_extra_cors_origins(cls, values: list[str]) -> list[str]:
        for value in values:
            if value == "*" or not value.startswith(("http://", "https://")):
                raise ValueError("CORS origins must be explicit http(s) URLs")
        return values


@lru_cache
def get_settings() -> Settings:
    return Settings()
