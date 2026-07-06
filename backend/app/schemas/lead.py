from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from app.schemas.run import AgentRunResponse

Tier = Literal["A", "B", "C"]
GateStatus = Literal["passed", "failed"]
DraftReviewStatus = Literal["needs_review", "copied", "exported"]
FactConfidence = Literal["high", "medium", "low", "fallback"]
GeoConfidence = Literal["high", "medium", "low"]
AssetTypeFit = Literal["multifamily", "student", "sfr", "commercial", "unclear"]
DomainStatus = Literal["corporate", "personal", "invalid", "unknown"]
DraftGenerationMode = Literal["llm", "fallback_template", "none"]
RelationshipType = Literal["company", "parent", "market", "submarket", "repeat_inbound"]


def _utc_now() -> datetime:
    return datetime.now(UTC)


class LeadCreate(BaseModel):
    contact_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    company: str = Field(min_length=1, max_length=180)
    role: str | None = Field(default=None, max_length=120)
    property_address: str = Field(min_length=1, max_length=240)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=2, max_length=80)
    country: str = Field(default="US", min_length=2, max_length=80)
    source: str | None = Field(default=None, max_length=120)
    submitted_at: datetime = Field(default_factory=_utc_now)


class SourceFact(BaseModel):
    source: str
    label: str
    value: str
    url: str | None = None
    retrieved_at: datetime | None = None
    confidence: FactConfidence | None = None


class GateResult(BaseModel):
    status: GateStatus
    failures: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class Enrichment(BaseModel):
    market: str
    coordinates: tuple[float, float] | None = None
    geo_confidence: GeoConfidence | None = None
    census_geo_id: str | None = None
    renter_share: float | None = None
    median_rent: int | None = None
    rent_growth_yoy: float | None = None
    household_growth: float | None = None
    unemployment_rate: float | None = None
    walkability_score: int | None = None
    company_units: int | None = None
    asset_type_fit: AssetTypeFit | None = None
    recent_trigger: str | None = None
    domain_status: DomainStatus | None = None
    sources: list[SourceFact] = Field(default_factory=list)


class ScoreComponent(BaseModel):
    name: str
    points: int
    rationale: str
    source_refs: list[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    total: int
    tier: Tier
    company_fit: int
    market_opportunity: int
    multipliers: list[str] = Field(default_factory=list)
    why_line: str
    components: list[ScoreComponent] = Field(default_factory=list)


class DraftEmail(BaseModel):
    subject: str
    body: str
    talking_points: list[str] = Field(default_factory=list)
    sources: list[SourceFact] = Field(default_factory=list)
    generation_mode: DraftGenerationMode = "fallback_template"
    review_status: DraftReviewStatus = "needs_review"


class RelatedLead(BaseModel):
    lead_id: str
    label: str
    reason: str
    relationship_type: RelationshipType
    score_impact: str | None = None


class LeadResponse(BaseModel):
    id: str
    input: LeadCreate
    gates: GateResult
    enrichment: Enrichment
    score: ScoreBreakdown
    talking_points: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    draft: DraftEmail | None = None
    related_leads: list[RelatedLead] = Field(default_factory=list)
    run_id: str
    run: AgentRunResponse | None = None


class SeedLeadResult(BaseModel):
    handle: str
    lead_id: str
    run_id: str
    tier: Tier
    gate_status: GateStatus
    draft_available: bool


class SeedLeadsResponse(BaseModel):
    reset: bool
    count: int
    seeds: list[SeedLeadResult]
