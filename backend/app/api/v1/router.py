from fastapi import APIRouter

from app.api.v1 import agents, health, leads


def build_api_router(*, include_demo_seed_routes: bool = False) -> APIRouter:
    router = APIRouter()
    router.include_router(health.router, tags=["health"])
    if include_demo_seed_routes:
        router.include_router(leads.seed_router, tags=["leads"])
    router.include_router(leads.router, prefix="/leads", tags=["leads"])
    router.include_router(agents.router, prefix="/agent-runs", tags=["agent-runs"])
    return router


api_router = build_api_router()
