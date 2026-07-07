from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.infrastructure.db.session import close_db_engine, create_db_schema


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    configure_logging(settings.log_level)
    should_create_schema = (
        settings.repository_backend == "postgres"
        and settings.create_db_schema_on_startup
    )
    if should_create_schema:
        await create_db_schema(settings)
    yield
    if settings.repository_backend == "postgres":
        await close_db_engine(settings)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    app = FastAPI(
        title="Signal API",
        version="0.1.0",
        description="Triggered inbound lead enrichment and scoring API.",
        lifespan=lifespan,
    )
    app.state.settings = app_settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
