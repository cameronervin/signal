from fastapi import APIRouter

from app.api.v1 import agents, health, leads

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(leads.seed_router, tags=["leads"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(agents.router, prefix="/agent-runs", tags=["agent-runs"])
