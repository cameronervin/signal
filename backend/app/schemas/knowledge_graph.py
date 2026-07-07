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
    lead_id: str
    label: str
    reason: str
    confidence: float = Field(ge=0, le=1)
    source_fact_ids: list[str] = Field(default_factory=list)


class KnowledgeGraphSource(BaseModel):
    id: str
    source: str
    label: str
    value: str
    url: str | None = None


class KnowledgeGraphContext(BaseModel):
    related_leads: list[KnowledgeGraphRelatedLead] = Field(default_factory=list)
    talking_points: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class LeadKnowledgeGraph(BaseModel):
    nodes: list[KnowledgeGraphNode] = Field(default_factory=list)
    edges: list[KnowledgeGraphEdge] = Field(default_factory=list)
    sources: list[KnowledgeGraphSource] = Field(default_factory=list)
    related_leads: list[KnowledgeGraphRelatedLead] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


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
