from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.graph_provider import (
    clear_signal_graph_provider_cache,
    get_signal_graph_provider,
)
from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.infrastructure.db.session import close_db_engine, get_sessionmaker
from app.infrastructure.knowledge_graph import create_knowledge_graph_service
from app.infrastructure.llm.factory import clear_llm_provider_cache, get_llm_provider
from app.infrastructure.public_data import (
    clear_public_data_client_cache,
    create_public_data_client,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    configure_logging(settings.log_level)
    logger.info("api_infrastructure_starting", env=settings.env, warm_only=True)
    http_client = httpx.AsyncClient(follow_redirects=True)
    try:
        sessionmaker = get_sessionmaker(settings)
        public_data_client = create_public_data_client(
            settings,
            http_client=http_client,
        )
        knowledge_graph_service = create_knowledge_graph_service(settings)
        llm_provider = get_llm_provider(settings)
        signal_graph_provider = get_signal_graph_provider(settings=settings)
        signal_graph_provider.signal_graph()
        app.state.http_client = http_client
        app.state.sessionmaker = sessionmaker
        app.state.public_data_client = public_data_client
        app.state.knowledge_graph_service = knowledge_graph_service
        app.state.llm_provider = llm_provider
        app.state.signal_graph_provider = signal_graph_provider
        logger.info(
            "api_infrastructure_initialized",
            env=settings.env,
            warm_only=True,
            components=[
                "db_sessionmaker",
                "http_client",
                "public_data_client",
                "knowledge_graph_service",
                "llm_provider",
                "signal_graph_provider",
            ],
        )
        yield
    finally:
        knowledge_graph_service = getattr(app.state, "knowledge_graph_service", None)
        if knowledge_graph_service is not None:
            await knowledge_graph_service.close()
        await http_client.aclose()
        await close_db_engine(settings)
        clear_public_data_client_cache()
        clear_llm_provider_cache()
        clear_signal_graph_provider_cache()
        logger.info(
            "api_infrastructure_shutdown_complete",
            env=settings.env,
            components=[
                "http_client",
                "db_engine",
                "knowledge_graph_service",
                "public_data_client_cache",
                "llm_provider_cache",
                "signal_graph_provider_cache",
            ],
        )


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
