"""Chain construction for Signal agent workflows."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain_core.tools import BaseTool

from app.agents.chains.outreach_drafting import (
    OUTREACH_DRAFT_CHAIN,
    create_outreach_draft_chain,
)
from app.core.config import Settings


def create_signal_pipeline_chain_set(
    *,
    settings: Settings,
    tools: Sequence[BaseTool] = (),
) -> dict[str, Any]:
    """Create the chains required by the Signal lead pipeline."""
    return {
        OUTREACH_DRAFT_CHAIN: create_outreach_draft_chain(
            settings=settings,
            tools=tools,
        )
    }
