"""Infrastructure adapters."""

from app.infrastructure.llm.factory import get_llm_provider

__all__ = ["get_llm_provider"]
