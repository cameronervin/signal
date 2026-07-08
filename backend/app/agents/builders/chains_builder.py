"""Chain construction for Signal agent workflows."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain_core.tools import BaseTool

from app.agents.chains.digital_worker import (
    DIGITAL_WORKER_DECISION_CHAIN,
    create_digital_worker_decision_chain,
)
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
        ),
    }


def create_digital_worker_chain_set(
    *,
    settings: Settings,
) -> dict[str, Any]:
    """Create the chains required by the SDR Digital Worker workflow."""
    return {
        DIGITAL_WORKER_DECISION_CHAIN: create_digital_worker_decision_chain(
            settings=settings,
        ),
    }
