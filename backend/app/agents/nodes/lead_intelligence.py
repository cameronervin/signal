from typing import Any

from langgraph.runtime import Runtime

from app.agents.chains.outreach_drafting import OUTREACH_DRAFT_CHAIN
from app.agents.guardrails.qualification import evaluate_gates
from app.agents.runtime_context import SignalRuntimeContext
from app.agents.states.signal_state import SignalState
from app.agents.tools.tool_registry import PUBLIC_DATA_ENRICHMENT_TOOL
from app.agents.utils.scoring import load_scoring_config, score_lead
from app.agents.utils.talking_points import talking_points_for_enrichment
from app.schemas.lead import RelatedLead

DETERMINISTIC_ENRICHMENT_NODE = "deterministic_enrichment"
DETERMINISTIC_SCORING_NODE = "deterministic_scoring"
AGENT_RESEARCH_AND_DRAFTING_NODE = "agent_research_and_drafting"
SCORING_AND_DRAFTING_NODE = AGENT_RESEARCH_AND_DRAFTING_NODE
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

    async def deterministic_scoring(
        state: SignalState,
        runtime: Runtime[SignalRuntimeContext],
    ) -> dict[str, Any]:
        lead = state["lead"]
        gates = state["gates"]
        enrichment = state["enrichment"]
        score = score_lead(
            lead,
            gates,
            enrichment,
            config=load_scoring_config(runtime.context.settings),
        )
        talking_points = talking_points_for_enrichment(enrichment)
        return {
            "score": score,
            "talking_points": talking_points,
            "activity_log": [
                *state.get("activity_log", []),
                "deterministic_scoring: completed",
            ],
        }

    async def agent_research_and_drafting(
        state: SignalState,
        runtime: Runtime[SignalRuntimeContext],
    ) -> dict[str, Any]:
        gates = state["gates"]
        draft = None
        flags = list(state.get("flags", []))
        activity_log = list(state.get("activity_log", []))
        if gates.status == "failed":
            return {
                "flags": flags,
                "draft": None,
                "activity_log": [
                    *activity_log,
                    "agent_research_and_drafting: skipped because gates failed",
                ],
            }
        try:
            draft_result = await chains[OUTREACH_DRAFT_CHAIN].ainvoke(
                {
                    "lead": state["lead"],
                    "gates": gates,
                    "enrichment": state["enrichment"],
                    "score": state["score"],
                    "talking_points": state["talking_points"],
                    "public_data_client": runtime.context.public_data_client,
                },
                config=_draft_chain_config(state),
            )
        except Exception:  # noqa: BLE001
            flags.append("model drafting failed")
            activity_log.append("agent_research_and_drafting: model drafting failed")
        else:
            draft = draft_result.draft
            for tool_name in dict.fromkeys(draft_result.tool_call_names):
                activity_log.append(
                    f"agent_research_and_drafting: called {tool_name}"
                )
            for warning in draft_result.warnings:
                flags.append(warning)
                activity_log.append(f"agent_research_and_drafting: {warning}")
            if draft is None:
                flags.append("model drafting returned no content")
                activity_log.append(
                    "agent_research_and_drafting: model returned no draft"
                )
        return {
            "flags": flags,
            "draft": draft,
            "activity_log": [
                *activity_log,
                "agent_research_and_drafting: completed",
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
                _human_review_activity(state),
            ],
        }

    return {
        DETERMINISTIC_ENRICHMENT_NODE: deterministic_enrichment,
        DETERMINISTIC_SCORING_NODE: deterministic_scoring,
        AGENT_RESEARCH_AND_DRAFTING_NODE: agent_research_and_drafting,
        KNOWLEDGE_GRAPH_NODE: knowledge_graph_builder,
    }


def _draft_chain_config(state: SignalState) -> dict[str, object]:
    return {
        "configurable": {
            "lead_id": state["lead_id"],
            "run_id": state["run_id"],
        }
    }


def _human_review_activity(state: SignalState) -> str:
    if state["gates"].status == "passed" and state.get("draft") is not None:
        return "human_review: awaiting approval"
    return "human_review: skipped because no draft was produced"
