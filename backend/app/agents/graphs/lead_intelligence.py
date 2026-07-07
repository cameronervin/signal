from langgraph.graph import END, START, StateGraph

from app.agents.nodes.lead_intelligence import (
    DETERMINISTIC_ENRICHMENT_NODE,
    KNOWLEDGE_GRAPH_NODE,
    SCORING_AND_DRAFTING_NODE,
)
from app.agents.runtime_context import SignalRuntimeContext
from app.agents.states.signal_state import SignalState


def create_lead_intelligence_graph(nodes: dict[str, object]) -> StateGraph:
    """Create the Signal lead pipeline topology without compiling it."""
    builder = StateGraph(SignalState, context_schema=SignalRuntimeContext)
    for name, node_fn in nodes.items():
        builder.add_node(name, node_fn)

    builder.add_edge(START, DETERMINISTIC_ENRICHMENT_NODE)
    builder.add_edge(DETERMINISTIC_ENRICHMENT_NODE, SCORING_AND_DRAFTING_NODE)
    builder.add_edge(SCORING_AND_DRAFTING_NODE, KNOWLEDGE_GRAPH_NODE)
    builder.add_edge(KNOWLEDGE_GRAPH_NODE, END)
    return builder
