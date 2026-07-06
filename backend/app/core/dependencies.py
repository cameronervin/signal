from functools import lru_cache

from app.repositories.memory import InMemorySignalRepository
from app.services.lead_service import LeadService


@lru_cache
def get_repository() -> InMemorySignalRepository:
    return InMemorySignalRepository()


def get_lead_service() -> LeadService:
    return LeadService(get_repository())
