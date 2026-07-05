from typing import NotRequired, TypedDict

from app.schemas.lead import (
    DraftEmail,
    Enrichment,
    GateResult,
    LeadCreate,
    RelatedLead,
    ScoreBreakdown,
)


class SignalState(TypedDict):
    lead_id: str
    run_id: str
    lead: LeadCreate
    gates: NotRequired[GateResult]
    enrichment: NotRequired[Enrichment]
    score: NotRequired[ScoreBreakdown]
    talking_points: NotRequired[list[str]]
    flags: NotRequired[list[str]]
    draft: NotRequired[DraftEmail | None]
    related_leads: NotRequired[list[RelatedLead]]
    activity_log: NotRequired[list[str]]
