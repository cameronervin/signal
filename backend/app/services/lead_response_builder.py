"""Lead response construction for Signal lead workflows."""

from app.agents.states.signal_state import SignalState
from app.schemas.lead import LeadCreate, LeadResponse


def build_lead_response(
    *,
    lead_id: str,
    run_id: str,
    lead: LeadCreate,
    result: SignalState,
) -> LeadResponse:
    """Build the API-facing lead snapshot from completed graph state."""
    return LeadResponse(
        id=lead_id,
        input=lead,
        gates=result["gates"],
        enrichment=result["enrichment"],
        score=result["score"],
        talking_points=result.get("talking_points", []),
        flags=result.get("flags", []),
        draft=result.get("draft"),
        related_leads=result.get("related_leads", []),
        run_id=run_id,
    )
