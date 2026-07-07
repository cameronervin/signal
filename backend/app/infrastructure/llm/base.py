from dataclasses import dataclass
from typing import Protocol

from langchain_core.tools import BaseTool

from app.infrastructure.public_data import PublicDataClient
from app.schemas.lead import (
    DraftEmail,
    Enrichment,
    GateResult,
    LeadCreate,
    ScoreBreakdown,
)


@dataclass(frozen=True, slots=True)
class DraftOutreachResult:
    draft: DraftEmail | None
    tool_call_names: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


class BaseLLMProvider(Protocol):
    provider_name: str

    async def draft_outreach(
        self,
        *,
        lead: LeadCreate,
        gates: GateResult,
        enrichment: Enrichment,
        score: ScoreBreakdown,
        talking_points: list[str],
        instructions: str,
        tools: list[BaseTool],
        public_data_client: PublicDataClient,
    ) -> DraftOutreachResult: ...
