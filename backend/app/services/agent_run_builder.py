"""Agent-run response construction for Signal lead workflows."""

from app.schemas.lead import LeadResponse
from app.schemas.run import AgentRunResponse, AgentStep


def build_agent_run_response(
    *,
    lead: LeadResponse,
    activity_log: list[str],
    trigger: str = "api_insert",
) -> AgentRunResponse:
    """Build the API-facing agent run snapshot for an enriched lead."""
    gates_passed = lead.gates.status == "passed"
    model_drafting_failed = gates_passed and lead.draft is None
    return AgentRunResponse(
        run_id=lead.run_id,
        lead_id=lead.id,
        status=(
            "failed"
            if model_drafting_failed
            else "awaiting_review"
            if gates_passed
            else "completed"
        ),
        trigger=trigger,
        current_stage=(
            "model_drafting_failed"
            if model_drafting_failed
            else "human_review"
            if gates_passed
            else "gate_failed"
        ),
        steps=[
            AgentStep(
                name="Deterministic enrichment",
                status="done",
                summary="Geography, market, company, and domain signals resolved.",
            ),
            AgentStep(
                name="Deterministic scoring",
                status="done",
                summary="Score, tier, why-line, and talking points computed.",
            ),
            AgentStep(
                name="Agent research and drafting",
                status=(
                    "failed"
                    if model_drafting_failed
                    else "done"
                    if gates_passed
                    else "skipped"
                ),
                summary=(
                    "Optional research completed and draft prepared."
                    if gates_passed
                    and not model_drafting_failed
                    else "Model drafting failed; no draft was produced."
                    if model_drafting_failed
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
                status=(
                    "pending"
                    if gates_passed and not model_drafting_failed
                    else "skipped"
                ),
                summary=(
                    "Awaiting SDR review before any outreach action."
                    if gates_passed
                    and not model_drafting_failed
                    else "Review skipped because no draft was produced."
                    if model_drafting_failed
                    else "Review skipped because hard gates failed."
                ),
            ),
        ],
        activity_log=activity_log,
    )
