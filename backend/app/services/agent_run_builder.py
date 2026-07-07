"""Agent-run response construction for Signal lead workflows."""

from app.schemas.lead import LeadResponse
from app.schemas.run import AgentRunResponse, AgentStep


def build_agent_run_response(
    *,
    lead: LeadResponse,
    activity_log: list[str],
) -> AgentRunResponse:
    """Build the API-facing agent run snapshot for an enriched lead."""
    gates_passed = lead.gates.status == "passed"
    return AgentRunResponse(
        run_id=lead.run_id,
        lead_id=lead.id,
        status="awaiting_review" if gates_passed else "completed",
        trigger="api_insert",
        current_stage="human_review" if gates_passed else "gate_failed",
        steps=[
            AgentStep(
                name="Deterministic enrichment",
                status="done",
                summary="Geography, market, company, and domain signals resolved.",
            ),
            AgentStep(
                name="Agent scoring and drafting",
                status="done" if gates_passed else "skipped",
                summary=(
                    "Score, why-line, talking points, and draft prepared."
                    if gates_passed
                    else "Draft suppressed because hard gates failed."
                ),
            ),
            AgentStep(
                name="Knowledge graph",
                status="done",
                summary="Related-lead context attached.",
            ),
            AgentStep(
                name="Human review",
                status="pending" if gates_passed else "skipped",
                summary="Awaiting SDR review before any outreach action.",
            ),
        ],
        activity_log=activity_log,
    )
