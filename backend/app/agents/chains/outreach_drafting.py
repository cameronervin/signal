"""LiteLLM-backed outreach drafting chain for Signal lead intelligence."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain_core.tools import BaseTool

from app.agents.prompts.outreach import OUTREACH_DRAFT_INSTRUCTIONS
from app.agents.tools.tool_prompts import TOOL_PROMPT_REGISTRY, ToolPromptKey
from app.core.config import Settings
from app.infrastructure.llm import get_llm_provider
from app.infrastructure.llm.base import BaseLLMProvider, DraftOutreachResult
from app.schemas.lead import (
    Enrichment,
    GateResult,
    LeadCreate,
    ScoreBreakdown,
)

OUTREACH_DRAFT_CHAIN = "outreach_draft"


class LiteLLMOutreachDraftChain:
    """Chain-shaped adapter around Signal's configured LLM provider."""

    def __init__(
        self,
        *,
        llm_provider: BaseLLMProvider,
        tools: Sequence[BaseTool],
    ) -> None:
        self.llm_provider = llm_provider
        self.tools = list(tools)
        self.instructions = _compose_instructions(self.tools)

    async def ainvoke(
        self,
        input: dict[str, Any],
        *,
        config: dict[str, object] | None = None,
        context: object | None = None,
    ) -> DraftOutreachResult:
        lead = input["lead"]
        gates = input["gates"]
        enrichment = input["enrichment"]
        score = input["score"]
        talking_points = input["talking_points"]
        public_data_client = input["public_data_client"]
        if (
            not isinstance(lead, LeadCreate)
            or not isinstance(gates, GateResult)
            or not isinstance(enrichment, Enrichment)
            or not isinstance(score, ScoreBreakdown)
            or not isinstance(talking_points, list)
            or public_data_client is None
        ):
            raise TypeError("Signal draft chain received invalid input types")
        return await self.llm_provider.draft_outreach(
            lead=lead,
            gates=gates,
            enrichment=enrichment,
            score=score,
            talking_points=talking_points,
            instructions=self.instructions,
            tools=self.tools,
            public_data_client=public_data_client,
        )


def create_outreach_draft_chain(
    *,
    settings: Settings,
    tools: Sequence[BaseTool] = (),
    llm_provider: BaseLLMProvider | None = None,
) -> LiteLLMOutreachDraftChain:
    """Create the configured model-backed outreach draft chain."""
    return LiteLLMOutreachDraftChain(
        llm_provider=llm_provider or get_llm_provider(settings),
        tools=tools,
    )


def _compose_instructions(tools: Sequence[BaseTool]) -> str:
    parts = [OUTREACH_DRAFT_INSTRUCTIONS]
    for tool in tools:
        snippet = TOOL_PROMPT_REGISTRY.get(
            ToolPromptKey(OUTREACH_DRAFT_CHAIN, tool.name)
        )
        if snippet:
            parts.append(snippet)
    return "\n".join(parts)
