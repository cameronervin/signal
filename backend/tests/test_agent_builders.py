from app.agents import builders
from app.agents.builders.chains_builder import create_signal_pipeline_chain_set
from app.agents.builders.nodes_builder import create_signal_pipeline_node_set
from app.agents.chains.outreach_drafting import OUTREACH_DRAFT_CHAIN
from app.agents.nodes import (
    DETERMINISTIC_ENRICHMENT_NODE,
    KNOWLEDGE_GRAPH_NODE,
    SCORING_AND_DRAFTING_NODE,
)
from app.agents.tools.tool_registry import (
    PUBLIC_DATA_ENRICHMENT_TOOL,
    create_signal_tool_set,
)
from app.core.config import Settings


def test_agent_builder_package_exports_stable_public_surface() -> None:
    assert builders.__all__ == [
        "compile_signal_pipeline_graph",
        "create_signal_pipeline_chain_set",
        "create_signal_pipeline_node_set",
    ]
    assert not hasattr(builders, "create_signal_pipeline_graph")
    assert not hasattr(builders, "create_signal_pipeline_nodes")


def test_signal_pipeline_builder_uses_named_chain_tool_and_node_keys() -> None:
    chains = create_signal_pipeline_chain_set(settings=Settings())
    tools = create_signal_tool_set()
    nodes = create_signal_pipeline_node_set(chains=chains)

    assert set(chains) == {OUTREACH_DRAFT_CHAIN}
    assert set(tools) == {PUBLIC_DATA_ENRICHMENT_TOOL}
    assert set(nodes) == {"signal_pipeline"}
    assert set(nodes["signal_pipeline"]) == {
        DETERMINISTIC_ENRICHMENT_NODE,
        SCORING_AND_DRAFTING_NODE,
        KNOWLEDGE_GRAPH_NODE,
    }
