"""Node-set construction for Signal agent workflows."""

from __future__ import annotations

from typing import Any

from app.agents.nodes.digital_worker import create_digital_worker_nodes
from app.agents.nodes.lead_intelligence import create_lead_intelligence_nodes
from app.agents.tools.tool_registry import create_signal_tool_set


def create_digital_worker_node_set(
    *,
    chains: dict[str, Any],
) -> dict[str, Any]:
    """Create the node set for the SDR Digital Worker workflow."""
    return create_digital_worker_nodes(chains=chains)


def create_signal_pipeline_node_set(
    *,
    chains: dict[str, Any],
) -> dict[str, Any]:
    """Create the node set for the Signal lead pipeline."""
    return create_lead_intelligence_nodes(
        chains=chains,
        tools=create_signal_tool_set(),
    )
