from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.knowledge_graph import LeadKnowledgeGraph
from app.schemas.run import AgentRunResponse

Tier = Literal["A", "B", "C"]
GateStatus = Literal["passed", "failed"]


class LeadCreate(BaseModel):
    contact_name: str = Field(
        min_length=1,
        max_length=120,
        description="Inbound contact name supplied for SDR lead follow-up.",
    )
    email: EmailStr = Field(
        description="Inbound contact email used for domain quality checks."
    )
    company: str = Field(
        min_length=1,
        max_length=180,
        description="Company or operator associated with the inbound lead.",
    )
    role: str | None = Field(
        default=None,
        max_length=120,
        description="Contact title used as a seniority and outreach context signal.",
    )
    property_address: str = Field(
        min_length=1,
        max_length=240,
        description="Managed property address used for public-data enrichment.",
    )
    city: str = Field(
        min_length=1,
        max_length=100,
        description="Property city used for market enrichment and lead scoring.",
    )
    state: str = Field(
        min_length=2,
        max_length=80,
        description="Property state used for market and economic enrichment.",
    )
    country: str = Field(
        default="US",
        min_length=2,
        max_length=80,
        description="Property country; v1 gates non-US leads out of draft outreach.",
    )


class SourceFact(BaseModel):
    source: str = Field(description="Public API or normalized source name.")
    label: str = Field(description="Rep-readable label for the citable fact.")
    value: str = Field(
        description="Citable value used to support scoring, insights, or outreach."
    )
    url: str | None = Field(
        default=None,
        description="Optional public URL for rep review of the source fact.",
    )


class GateResult(BaseModel):
    status: GateStatus = Field(
        description="Whether the inbound lead passed hard outreach-safety gates."
    )
    failures: list[str] = Field(
        default_factory=list,
        description="Hard gate reasons that suppress draft outreach.",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-blocking lead quality or provider concerns for rep review.",
    )


class Enrichment(BaseModel):
    market: str = Field(
        description="Resolved property market used for scoring and sales insights."
    )
    coordinates: tuple[float, float] | None = Field(
        default=None,
        description="Optional geocoded property coordinates from public data.",
    )
    renter_share: float | None = Field(
        default=None,
        description="Market renter share used as a leasing demand signal.",
    )
    median_rent: int | None = Field(
        default=None,
        description="Market rent context for rep review and outreach grounding.",
    )
    rent_growth_yoy: float | None = Field(
        default=None,
        description="Year-over-year rent growth used as a market urgency signal.",
    )
    household_growth: float | None = Field(
        default=None,
        description="Household growth used as demand expansion context.",
    )
    unemployment_rate: float | None = Field(
        default=None,
        description="Labor-market context used as an operational pressure proxy.",
    )
    company_units: int | None = Field(
        default=None,
        description="Portfolio scale signal for fit and follow-up complexity.",
    )
    recent_trigger: str | None = Field(
        default=None,
        description="Recent company or market trigger for cited personalization.",
    )
    sources: list[SourceFact] = Field(
        default_factory=list,
        description="Citable public-data facts supporting scoring and outreach.",
    )
    provider_warnings: list[str] = Field(
        default_factory=list,
        description="Explicit public-data provider failures or missing-data notes.",
    )


class ScoreBreakdown(BaseModel):
    total: int = Field(description="Server-generated 0-100 lead priority score.")
    tier: Tier = Field(description="Lead priority band for SDR queue ordering.")
    company_fit: int = Field(
        description="Company and contact fit points in the lead scoring rubric."
    )
    market_opportunity: int = Field(
        description="Market opportunity points from public-data enrichment."
    )
    bonuses: int = Field(description="Bounded bonus points from trigger signals.")
    why_line: str = Field(
        description="Rep-readable explanation of the top score drivers."
    )
    components: dict[str, int] = Field(
        description="Inspectible score components for calibration and review."
    )


class DraftEmail(BaseModel):
    subject: str = Field(description="Review-ready draft subject line.")
    body: str = Field(
        description="Review-ready inbound outreach body for SDR editing."
    )
    sources: list[SourceFact] = Field(
        default_factory=list,
        description="Source facts that support draft personalization claims.",
    )


class RelatedLead(BaseModel):
    lead_id: str = Field(description="Related lead identifier for graph context.")
    label: str = Field(description="Rep-readable related lead label.")
    reason: str = Field(
        description="Why the related lead may help prioritize or personalize outreach."
    )


class LeadResponse(BaseModel):
    id: UUID = Field(description="Lead snapshot id.")
    input: LeadCreate = Field(description="Original inbound lead input.")
    gates: GateResult = Field(
        description="Qualification gate output controlling draft eligibility."
    )
    enrichment: Enrichment = Field(
        description="Public API enrichment for scoring, insights, and drafting."
    )
    score: ScoreBreakdown = Field(
        description="Lead scoring output used to prioritize SDR follow-up."
    )
    talking_points: list[str] = Field(
        default_factory=list,
        description=(
            "Sales insights derived from enrichment and graph context for "
            "rep review and draft personalization."
        ),
    )
    flags: list[str] = Field(
        default_factory=list,
        description="Gate failures, warnings, and provider notes for rep review.",
    )
    draft: DraftEmail | None = Field(
        default=None,
        description="Review-ready outreach draft, omitted when hard gates fail.",
    )
    related_leads: list[RelatedLead] = Field(
        default_factory=list,
        description="Related inbound context that can aid prioritization.",
    )
    knowledge_graph: LeadKnowledgeGraph = Field(
        default_factory=LeadKnowledgeGraph,
        description=(
            "Graph context linking lead, company, property, sources, and triggers."
        ),
    )
    run_id: UUID = Field(description="Agent run id that produced this lead output.")


class LeadQueueItemResponse(BaseModel):
    id: UUID = Field(description="Lead id used for row identity.")
    run_id: UUID = Field(description="Agent run id associated with the row.")
    state: Literal["ready", "loading"] = Field(
        description="Whether the row has completed lead analysis or is still running."
    )
    input: LeadCreate = Field(description="Submitted inbound lead input.")
    lead: LeadResponse | None = Field(
        default=None,
        description="Completed lead analysis when the row is ready.",
    )
    run: AgentRunResponse | None = Field(
        default=None,
        description="Current agent run status while the row is loading.",
    )


class LeadDeleteResponse(BaseModel):
    deleted_leads: int = Field(
        description="Number of completed lead snapshots deleted."
    )
    deleted_agent_runs: int = Field(
        description="Number of lead-intelligence agent runs deleted."
    )
    deleted_status_events: int = Field(
        description="Number of agent run status events deleted."
    )
    skipped_assigned_leads: int = Field(
        default=0,
        description="Active or paused Digital Workforce lead assignments skipped.",
    )
