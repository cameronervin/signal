"""Graph compilation for Signal agent workflows."""

from __future__ import annotations

from typing import Any

from app.agents.builders.chains_builder import create_signal_pipeline_chain_set
from app.agents.builders.nodes_builder import create_signal_pipeline_node_set
from app.agents.graphs.lead_intelligence import create_lead_intelligence_graph
from app.core.config import Settings


def compose_signal_pipeline_dependencies(
    *,
    app_settings: Settings,
) -> dict[str, Any]:
    """Create the Signal pipeline's chains and nodes."""
    chains = create_signal_pipeline_chain_set(settings=app_settings)
    nodes = create_signal_pipeline_node_set(chains=chains)
    return nodes


def compile_signal_pipeline_graph(
    *,
    app_settings: Settings,
    checkpointer: Any | None = None,
) -> Any:
    """Build and compile the Signal lead pipeline graph."""
    nodes = compose_signal_pipeline_dependencies(app_settings=app_settings)
    graph_builder = create_lead_intelligence_graph(nodes=nodes["signal_pipeline"])
    return graph_builder.compile(checkpointer=checkpointer)
