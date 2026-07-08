from typing import Literal

from pydantic import BaseModel, Field

KnowledgeGraphNodeKind = Literal[
    "lead",
    "contact",
    "company",
    "property",
    "market",
    "source_fact",
    "trigger",
]

KnowledgeGraphRelationship = Literal[
    "HAS_CONTACT",
    "WORKS_AT",
    "ABOUT_PROPERTY",
    "IN_MARKET",
    "HAS_SOURCE_FACT",
    "HAS_TRIGGER",
    "RELATED_TO",
]


class KnowledgeGraphNode(BaseModel):
    id: str
    kind: KnowledgeGraphNodeKind
    label: str
    subtitle: str | None = None
    source_fact_ids: list[str] = Field(default_factory=list)


class KnowledgeGraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relationship: KnowledgeGraphRelationship
    reason: str
    confidence: float = Field(ge=0, le=1)
    source_fact_ids: list[str] = Field(default_factory=list)


class KnowledgeGraphRelatedLead(BaseModel):
    lead_id: str = Field(description="Related inbound lead identifier.")
    label: str = Field(description="Rep-readable related lead label.")
    reason: str = Field(description="Reason this lead is related for SDR review.")
    confidence: float = Field(
        ge=0,
        le=1,
        description="Relationship confidence for prioritization context.",
    )
    source_fact_ids: list[str] = Field(
        default_factory=list,
        description="Source fact ids supporting the related-lead signal.",
    )


class KnowledgeGraphSource(BaseModel):
    id: str
    source: str
    label: str
    value: str
    url: str | None = None


class KnowledgeGraphContext(BaseModel):
    related_leads: list[KnowledgeGraphRelatedLead] = Field(default_factory=list)
    talking_points: list[str] = Field(
        default_factory=list,
        description="Graph-derived sales insights exposed through talking_points.",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Graph storage or retrieval warnings for rep review.",
    )


class LeadKnowledgeGraph(BaseModel):
    nodes: list[KnowledgeGraphNode] = Field(
        default_factory=list,
        description=(
            "Bounded graph nodes for lead, company, property, market, and facts."
        ),
    )
    edges: list[KnowledgeGraphEdge] = Field(
        default_factory=list,
        description="Explainable relationships that support SDR context.",
    )
    sources: list[KnowledgeGraphSource] = Field(
        default_factory=list,
        description="Citable graph source facts for review and personalization.",
    )
    related_leads: list[KnowledgeGraphRelatedLead] = Field(
        default_factory=list,
        description="Related inbound lead context for prioritization.",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Graph storage or retrieval warnings for rep review.",
    )


class KnowledgeGraphLeadRecord(BaseModel):
    lead_id: str
    label: str
    company: str
    company_normalized: str
    property_address: str
    property_normalized: str
    market: str
    market_normalized: str
    trigger: str | None = None
    trigger_normalized: str | None = None
    source_fact_ids: list[str] = Field(default_factory=list)
    source_categories: list[str] = Field(default_factory=list)


class KnowledgeGraphRelatedCandidate(BaseModel):
    lead_id: str
    label: str
    company_normalized: str | None = None
    property_normalized: str | None = None
    market_normalized: str | None = None
    trigger_normalized: str | None = None
    source_fact_ids: list[str] = Field(default_factory=list)
    source_categories: list[str] = Field(default_factory=list)
