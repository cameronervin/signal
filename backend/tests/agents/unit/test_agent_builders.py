from app.agents import builders
from app.agents.builders.chains_builder import (
    create_digital_worker_chain_set,
    create_signal_pipeline_chain_set,
)
from app.agents.builders.graphs_builder import (
    compose_digital_worker_dependencies,
    compose_signal_pipeline_dependencies,
)
from app.agents.builders.nodes_builder import (
    create_digital_worker_node_set,
    create_signal_pipeline_node_set,
)
from app.agents.chains.digital_worker import DIGITAL_WORKER_DECISION_CHAIN
from app.agents.chains.outreach_drafting import OUTREACH_DRAFT_CHAIN
from app.agents.nodes import (
    DETERMINISTIC_ENRICHMENT_NODE,
    DETERMINISTIC_SCORING_NODE,
    DIGITAL_WORKER_ACTION_NODE,
    DIGITAL_WORKER_CONTEXT_NODE,
    GRAPH_CONTEXT_RETRIEVAL_NODE,
    KNOWLEDGE_GRAPH_INGEST_NODE,
    KNOWLEDGE_GRAPH_NODE,
    SCORING_AND_DRAFTING_NODE,
)
from app.agents.prompts.digital_worker import digital_worker_tool_prompt
from app.agents.tools.digital_worker import (
    DIGITAL_WORKER_MARK_GOAL_COMPLETE_TOOL,
    DIGITAL_WORKER_MARK_PHASE_OUTCOME_TOOL,
    DIGITAL_WORKER_RECORD_INBOUND_EMAIL_TOOL,
    DIGITAL_WORKER_SCHEDULE_FOLLOW_UP_TOOL,
    DIGITAL_WORKER_SEND_SANDBOX_EMAIL_TOOL,
)
from app.agents.tools.tool_registry import (
    PUBLIC_DATA_ENRICHMENT_TOOL,
    create_digital_worker_tool_registry,
    create_signal_tool_set,
)
from app.core.config import Settings


def test_agent_builder_package_exports_stable_public_surface() -> None:
    assert builders.__all__ == [
        "compile_digital_worker_graph",
        "compile_signal_pipeline_graph",
        "compose_digital_worker_dependencies",
        "compose_signal_pipeline_dependencies",
        "create_digital_worker_chain_set",
        "create_digital_worker_node_set",
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
    assert set(nodes) == {
        DETERMINISTIC_ENRICHMENT_NODE,
        KNOWLEDGE_GRAPH_INGEST_NODE,
        GRAPH_CONTEXT_RETRIEVAL_NODE,
        DETERMINISTIC_SCORING_NODE,
        SCORING_AND_DRAFTING_NODE,
        KNOWLEDGE_GRAPH_NODE,
    }


def test_digital_worker_builder_uses_named_chain_and_node_keys() -> None:
    chains = create_digital_worker_chain_set(settings=Settings())
    nodes = create_digital_worker_node_set(chains=chains)

    assert set(chains) == {DIGITAL_WORKER_DECISION_CHAIN}
    assert set(nodes) == {
        DIGITAL_WORKER_CONTEXT_NODE,
        DIGITAL_WORKER_ACTION_NODE,
    }


def test_workflow_dependency_composers_keep_graph_inputs_separate() -> None:
    settings = Settings()

    signal_dependencies = compose_signal_pipeline_dependencies(app_settings=settings)
    digital_dependencies = compose_digital_worker_dependencies(app_settings=settings)

    assert set(signal_dependencies) == {"chains", "nodes"}
    assert set(digital_dependencies) == {"chains", "nodes"}
    assert set(signal_dependencies["chains"]) == {OUTREACH_DRAFT_CHAIN}
    assert set(digital_dependencies["chains"]) == {DIGITAL_WORKER_DECISION_CHAIN}
    assert DIGITAL_WORKER_CONTEXT_NODE not in signal_dependencies["nodes"]
    assert DETERMINISTIC_ENRICHMENT_NODE not in digital_dependencies["nodes"]


def test_digital_worker_tool_registry_and_prompt_are_registered() -> None:
    registry = create_digital_worker_tool_registry()
    prompt = digital_worker_tool_prompt()

    assert set(registry) == {
        DIGITAL_WORKER_SEND_SANDBOX_EMAIL_TOOL,
        DIGITAL_WORKER_RECORD_INBOUND_EMAIL_TOOL,
        DIGITAL_WORKER_SCHEDULE_FOLLOW_UP_TOOL,
        DIGITAL_WORKER_MARK_GOAL_COMPLETE_TOOL,
        DIGITAL_WORKER_MARK_PHASE_OUTCOME_TOOL,
    }
    assert DIGITAL_WORKER_SEND_SANDBOX_EMAIL_TOOL in prompt
    assert "never calls a live email provider" in prompt
