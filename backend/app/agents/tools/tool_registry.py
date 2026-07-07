"""Tool registry for Signal agent workflows."""

from __future__ import annotations

from typing import Any

from app.agents.tools.public_data import enrich_lead_with_public_data

PUBLIC_DATA_ENRICHMENT_TOOL = "public_data_enrichment"


def create_signal_tool_set() -> dict[str, Any]:
    """Return the deterministic tools used by the Signal pipeline."""
    return {PUBLIC_DATA_ENRICHMENT_TOOL: enrich_lead_with_public_data}
