from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.services.lead_service import LeadService, get_lead_service


def build_lifespan(settings: Settings):
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_logging(settings.log_level)
        app.state.settings = settings
        yield

    return lifespan


def create_app(
    settings: Settings | None = None,
    lead_service: LeadService | None = None,
) -> FastAPI:
    app_settings = settings or get_settings()
    app = FastAPI(
        title="Signal API",
        version="0.1.0",
        description="Triggered inbound lead enrichment and scoring API.",
        lifespan=build_lifespan(app_settings),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
    app.dependency_overrides[get_settings] = lambda: app_settings
    if lead_service is not None:
        async def override_lead_service() -> LeadService:
            return lead_service

        app.dependency_overrides[get_lead_service] = override_lead_service
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
