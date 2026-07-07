from functools import lru_cache

from app.core.config import Settings, get_settings
from app.infrastructure.public_data.provider import (
    PublicDataClient,
    PublicDataClientConfig,
)


@lru_cache
def _cached_public_data_client(settings_json: str) -> PublicDataClient:
    settings = Settings.model_validate_json(settings_json)
    return PublicDataClient(
        PublicDataClientConfig(
            news_api_key=settings.news_api_key,
            fred_api_key=settings.fred_api_key,
            census_api_key=settings.census_api_key,
            user_agent=settings.public_data_user_agent,
            nominatim_email=settings.nominatim_email,
            cache_ttl_seconds=settings.public_data_cache_ttl_seconds,
        )
    )


def get_public_data_client(settings: Settings | None = None) -> PublicDataClient:
    app_settings = settings or get_settings()
    return _cached_public_data_client(app_settings.model_dump_json())


def clear_public_data_client_cache() -> None:
    _cached_public_data_client.cache_clear()
