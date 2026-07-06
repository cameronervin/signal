from langgraph.graph import END, START, StateGraph

from app.agents.nodes import (
    agent_scoring_and_drafting_node,
    deterministic_enrichment_node,
    knowledge_graph_builder_node,
)
from app.agents.state import SignalState


def build_signal_graph():
    graph = StateGraph(SignalState)
    graph.add_node("deterministic_enrichment", deterministic_enrichment_node)
    graph.add_node("agent_scoring_and_drafting", agent_scoring_and_drafting_node)
    graph.add_node("knowledge_graph_builder", knowledge_graph_builder_node)
    graph.add_edge(START, "deterministic_enrichment")
    graph.add_edge("deterministic_enrichment", "agent_scoring_and_drafting")
    graph.add_edge("agent_scoring_and_drafting", "knowledge_graph_builder")
    graph.add_edge("knowledge_graph_builder", END)
    return graph.compile()


async def run_signal_pipeline(initial_state: SignalState) -> SignalState:
    graph = build_signal_graph()
    result = await graph.ainvoke(initial_state)
    return result
