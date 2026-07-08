from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.knowledge_graph import LeadKnowledgeGraph

Tier = Literal["A", "B", "C"]
GateStatus = Literal["passed", "failed"]


class LeadCreate(BaseModel):
    contact_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    company: str = Field(min_length=1, max_length=180)
    role: str | None = Field(default=None, max_length=120)
    property_address: str = Field(min_length=1, max_length=240)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=2, max_length=80)
    country: str = Field(default="US", min_length=2, max_length=80)


class SourceFact(BaseModel):
    source: str
    label: str
    value: str
    url: str | None = None


class GateResult(BaseModel):
    status: GateStatus
    failures: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class Enrichment(BaseModel):
    market: str
    coordinates: tuple[float, float] | None = None
    renter_share: float | None = None
    median_rent: int | None = None
    rent_growth_yoy: float | None = None
    household_growth: float | None = None
    unemployment_rate: float | None = None
    company_units: int | None = None
    recent_trigger: str | None = None
    sources: list[SourceFact] = Field(default_factory=list)
    provider_warnings: list[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    total: int
    tier: Tier
    company_fit: int
    market_opportunity: int
    bonuses: int
    why_line: str
    components: dict[str, int]


class DraftEmail(BaseModel):
    subject: str
    body: str
    sources: list[SourceFact] = Field(default_factory=list)


class RelatedLead(BaseModel):
    lead_id: str
    label: str
    reason: str


class LeadResponse(BaseModel):
    id: UUID
    input: LeadCreate
    gates: GateResult
    enrichment: Enrichment
    score: ScoreBreakdown
    talking_points: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    draft: DraftEmail | None = None
    related_leads: list[RelatedLead] = Field(default_factory=list)
    knowledge_graph: LeadKnowledgeGraph = Field(default_factory=LeadKnowledgeGraph)
    run_id: UUID
