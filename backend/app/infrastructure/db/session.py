from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings, get_settings
from app.infrastructure.db.base import Base

_engine_cache: dict[str, AsyncEngine] = {}
_sessionmaker_cache: dict[str, async_sessionmaker[AsyncSession]] = {}


def get_engine(settings: Settings | None = None) -> AsyncEngine:
    app_settings = settings or get_settings()
    database_url = app_settings.database_url
    if database_url not in _engine_cache:
        _engine_cache[database_url] = create_async_engine(
            database_url,
            pool_pre_ping=True,
        )
    return _engine_cache[database_url]


def get_sessionmaker(
    settings: Settings | None = None,
) -> async_sessionmaker[AsyncSession]:
    app_settings = settings or get_settings()
    database_url = app_settings.database_url
    if database_url not in _sessionmaker_cache:
        _sessionmaker_cache[database_url] = async_sessionmaker(
            get_engine(app_settings),
            expire_on_commit=False,
        )
    return _sessionmaker_cache[database_url]


async def create_db_schema(settings: Settings | None = None) -> None:
    from app.models import signal  # noqa: F401

    engine = get_engine(settings)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def close_db_engine(settings: Settings | None = None) -> None:
    app_settings = settings or get_settings()
    database_url = app_settings.database_url
    engine = _engine_cache.pop(database_url, None)
    _sessionmaker_cache.pop(database_url, None)
    if engine is not None:
        await engine.dispose()
