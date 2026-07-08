from langgraph.graph import END, START, StateGraph

from app.agents.nodes.digital_worker import (
    DIGITAL_WORKER_ACTION_NODE,
    DIGITAL_WORKER_CONTEXT_NODE,
)
from app.agents.runtime_context import DigitalWorkerRuntimeContext
from app.agents.states.digital_worker_state import DigitalWorkerState


def create_digital_worker_graph(nodes: dict[str, object]) -> StateGraph:
    """Create the SDR Digital Worker graph topology without compiling it."""
    builder = StateGraph(
        DigitalWorkerState,
        context_schema=DigitalWorkerRuntimeContext,
    )
    for name, node_fn in nodes.items():
        builder.add_node(name, node_fn)

    builder.add_edge(START, DIGITAL_WORKER_CONTEXT_NODE)
    builder.add_edge(DIGITAL_WORKER_CONTEXT_NODE, DIGITAL_WORKER_ACTION_NODE)
    builder.add_edge(DIGITAL_WORKER_ACTION_NODE, END)
    return builder
