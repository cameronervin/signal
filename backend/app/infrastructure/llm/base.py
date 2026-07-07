from typing import Protocol

from app.schemas.lead import DraftEmail, Enrichment, LeadCreate


class BaseLLMProvider(Protocol):
    provider_name: str

    async def draft_outreach(
        self,
        *,
        lead: LeadCreate,
        enrichment: Enrichment,
        instructions: str,
    ) -> DraftEmail | None: ...
