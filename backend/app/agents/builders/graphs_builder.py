"""Graph compilation for Signal agent workflows."""

from __future__ import annotations

from typing import Any

from app.agents.builders.chains_builder import (
    create_digital_worker_chain_set,
    create_signal_pipeline_chain_set,
)
from app.agents.builders.nodes_builder import (
    create_digital_worker_node_set,
    create_signal_pipeline_node_set,
)
from app.agents.graphs.digital_worker import create_digital_worker_graph
from app.agents.graphs.lead_intelligence import create_lead_intelligence_graph
from app.agents.tools.tool_assignment import (
    build_workflow_chain_tool_map,
    resolve_active_tools,
)
from app.agents.tools.tool_registry import ToolBuildContext
from app.core.config import Settings


def compose_signal_pipeline_dependencies(
    *,
    app_settings: Settings,
) -> dict[str, Any]:
    """Create the Signal pipeline's chains and nodes."""
    active_tools = resolve_active_tools(ToolBuildContext(settings=app_settings))
    chain_tool_map = build_workflow_chain_tool_map(active_tools)
    outreach_tools = chain_tool_map["signal_pipeline"]["outreach_draft"]
    chains = create_signal_pipeline_chain_set(
        settings=app_settings,
        tools=outreach_tools,
    )
    nodes = create_signal_pipeline_node_set(chains=chains)
    return {"chains": chains, "nodes": nodes}


def compose_digital_worker_dependencies(
    *,
    app_settings: Settings,
) -> dict[str, Any]:
    """Create the SDR Digital Worker's chains and nodes."""
    chains = create_digital_worker_chain_set(settings=app_settings)
    nodes = create_digital_worker_node_set(chains=chains)
    return {"chains": chains, "nodes": nodes}


def compile_signal_pipeline_graph(
    *,
    app_settings: Settings,
    checkpointer: Any | None = None,
) -> Any:
    """Build and compile the Signal lead pipeline graph."""
    dependencies = compose_signal_pipeline_dependencies(app_settings=app_settings)
    graph_builder = create_lead_intelligence_graph(nodes=dependencies["nodes"])
    return graph_builder.compile(checkpointer=checkpointer)


def compile_digital_worker_graph(
    *,
    app_settings: Settings,
    checkpointer: Any | None = None,
) -> Any:
    """Build and compile the SDR Digital Worker graph."""
    dependencies = compose_digital_worker_dependencies(app_settings=app_settings)
    graph_builder = create_digital_worker_graph(nodes=dependencies["nodes"])
    return graph_builder.compile(checkpointer=checkpointer)
