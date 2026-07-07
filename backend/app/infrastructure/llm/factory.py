from functools import lru_cache

from app.core.config import Settings, get_settings
from app.infrastructure.llm.base import BaseLLMProvider
from app.infrastructure.llm.litellm import LiteLLMProvider


@lru_cache
def _cached_litellm_provider(settings_json: str) -> LiteLLMProvider:
    return LiteLLMProvider(Settings.model_validate_json(settings_json))


def get_llm_provider(settings: Settings | None = None) -> BaseLLMProvider:
    app_settings = settings or get_settings()
    return _cached_litellm_provider(app_settings.model_dump_json())


def clear_llm_provider_cache() -> None:
    _cached_litellm_provider.cache_clear()
