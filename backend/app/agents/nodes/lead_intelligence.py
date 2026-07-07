from typing import Any

from langgraph.runtime import Runtime

from app.agents.chains.outreach_drafting import OUTREACH_DRAFT_CHAIN
from app.agents.guardrails.qualification import evaluate_gates
from app.agents.runtime_context import SignalRuntimeContext
from app.agents.states.signal_state import SignalState
from app.agents.tools.tool_registry import PUBLIC_DATA_ENRICHMENT_TOOL
from app.agents.utils.scoring import score_lead
from app.agents.utils.talking_points import talking_points_for_enrichment
from app.schemas.lead import RelatedLead

DETERMINISTIC_ENRICHMENT_NODE = "deterministic_enrichment"
SCORING_AND_DRAFTING_NODE = "agent_scoring_and_drafting"
KNOWLEDGE_GRAPH_NODE = "knowledge_graph_builder"


def create_lead_intelligence_nodes(
    *,
    chains: dict[str, Any],
    tools: dict[str, Any],
) -> dict[str, Any]:
    """Create all nodes needed by the Signal lead pipeline graph."""

    async def deterministic_enrichment(
        state: SignalState,
        runtime: Runtime[SignalRuntimeContext],
    ) -> dict[str, Any]:
        lead = state["lead"]
        enrichment = await tools[PUBLIC_DATA_ENRICHMENT_TOOL](
            public_data_client=runtime.context.public_data_client,
            lead=lead,
        )
        gates = evaluate_gates(lead, enrichment)
        flags = [*gates.failures, *gates.warnings]
        return {
            "enrichment": enrichment,
            "gates": gates,
            "flags": flags,
            "activity_log": ["deterministic_enrichment: completed"],
        }

    async def agent_scoring_and_drafting(state: SignalState) -> dict[str, Any]:
        lead = state["lead"]
        gates = state["gates"]
        enrichment = state["enrichment"]
        score = score_lead(lead, gates, enrichment)
        talking_points = talking_points_for_enrichment(enrichment)
        draft = (
            None
            if gates.status == "failed"
            else await chains[OUTREACH_DRAFT_CHAIN].ainvoke(
                {
                    "lead": lead,
                    "enrichment": enrichment,
                },
                config=_draft_chain_config(state),
            )
        )
        return {
            "score": score,
            "talking_points": talking_points,
            "draft": draft,
            "activity_log": [
                *state.get("activity_log", []),
                "agent_scoring_and_drafting: completed",
            ],
        }

    async def knowledge_graph_builder(state: SignalState) -> dict[str, Any]:
        lead = state["lead"]
        related = [
            RelatedLead(
                lead_id="demo-related-001",
                label=f"{lead.company} related inbound",
                reason="Same company appeared in fixture history",
            )
        ]
        return {
            "related_leads": related,
            "activity_log": [
                *state.get("activity_log", []),
                "knowledge_graph_builder: completed",
                "human_review: awaiting approval",
            ],
        }

    return {
        DETERMINISTIC_ENRICHMENT_NODE: deterministic_enrichment,
        SCORING_AND_DRAFTING_NODE: agent_scoring_and_drafting,
        KNOWLEDGE_GRAPH_NODE: knowledge_graph_builder,
    }


def _draft_chain_config(state: SignalState) -> dict[str, object]:
    return {
        "configurable": {
            "lead_id": state["lead_id"],
            "run_id": state["run_id"],
        }
    }
