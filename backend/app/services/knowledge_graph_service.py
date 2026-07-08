from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from typing import Protocol

from app.schemas.knowledge_graph import (
    KnowledgeGraphContext,
    KnowledgeGraphEdge,
    KnowledgeGraphLeadRecord,
    KnowledgeGraphNode,
    KnowledgeGraphRelatedCandidate,
    KnowledgeGraphRelatedLead,
    KnowledgeGraphSource,
    LeadKnowledgeGraph,
)
from app.schemas.lead import Enrichment, LeadCreate

_NON_WORD_RE = re.compile(r"[^a-z0-9]+")
_SPACE_RE = re.compile(r"\s+")


def normalize_entity(value: str | None) -> str:
    """Return a stable, low-cardinality key for graph entity matching."""
    if not value:
        return ""
    lower = value.casefold().strip()
    words = _NON_WORD_RE.sub(" ", lower)
    return _SPACE_RE.sub(" ", words).strip()


def graph_node_id(kind: str, value: str) -> str:
    normalized = normalize_entity(value)
    digest = hashlib.sha1(f"{kind}:{normalized}".encode()).hexdigest()[:16]
    return f"{kind}:{digest}"


class KnowledgeGraphRepository(Protocol):
    async def ingest_lead_graph(
        self,
        record: KnowledgeGraphLeadRecord,
        graph: LeadKnowledgeGraph,
    ) -> None: ...

    async def find_related_leads(
        self,
        record: KnowledgeGraphLeadRecord,
    ) -> list[KnowledgeGraphRelatedCandidate]: ...

    async def close(self) -> None: ...


class KnowledgeGraphService:
    def __init__(
        self,
        repository: KnowledgeGraphRepository,
        *,
        storage_enabled: bool,
    ) -> None:
        self.repository = repository
        self.storage_enabled = storage_enabled

    async def ingest_lead_graph(
        self,
        *,
        lead_id: str,
        lead: LeadCreate,
        enrichment: Enrichment,
    ) -> KnowledgeGraphContext:
        warnings = _disabled_warnings(self.storage_enabled)
        if not self.storage_enabled:
            return KnowledgeGraphContext(warnings=warnings)

        record = build_lead_graph_record(
            lead_id=lead_id,
            lead=lead,
            enrichment=enrichment,
        )
        graph = project_lead_graph(
            lead_id=lead_id,
            lead=lead,
            enrichment=enrichment,
            graph_context=KnowledgeGraphContext(),
        )
        try:
            await self.repository.ingest_lead_graph(record, graph)
        except Exception:  # noqa: BLE001
            warnings.append(
                "knowledge graph storage unavailable; returned current lead graph only"
            )
        return KnowledgeGraphContext(warnings=dedupe(warnings))

    async def retrieve_graph_context(
        self,
        *,
        lead_id: str,
        lead: LeadCreate,
        enrichment: Enrichment,
        existing_warnings: Iterable[str] = (),
    ) -> KnowledgeGraphContext:
        warnings = [*existing_warnings, *_disabled_warnings(self.storage_enabled)]
        record = build_lead_graph_record(
            lead_id=lead_id,
            lead=lead,
            enrichment=enrichment,
        )
        candidates: list[KnowledgeGraphRelatedCandidate] = []
        if self.storage_enabled:
            try:
                candidates = await self.repository.find_related_leads(record)
            except Exception:  # noqa: BLE001
                warnings.append(
                    "knowledge graph retrieval unavailable; returned current "
                    "lead graph only"
                )
        related = related_leads_for_record(record, candidates)
        return KnowledgeGraphContext(
            related_leads=related,
            talking_points=graph_talking_points(related),
            warnings=dedupe(warnings),
        )

    def project_lead_graph(
        self,
        *,
        lead_id: str,
        lead: LeadCreate,
        enrichment: Enrichment,
        graph_context: KnowledgeGraphContext | None = None,
    ) -> LeadKnowledgeGraph:
        return project_lead_graph(
            lead_id=lead_id,
            lead=lead,
            enrichment=enrichment,
            graph_context=graph_context or KnowledgeGraphContext(),
        )

    async def close(self) -> None:
        await self.repository.close()


def build_lead_graph_record(
    *,
    lead_id: str,
    lead: LeadCreate,
    enrichment: Enrichment,
) -> KnowledgeGraphLeadRecord:
    source_ids = [_source_id(source) for source in enrichment.sources]
    market = enrichment.market or f"{lead.city}, {lead.state}"
    return KnowledgeGraphLeadRecord(
        lead_id=lead_id,
        label=f"{lead.contact_name} at {lead.company}",
        company=lead.company,
        company_normalized=normalize_entity(lead.company),
        property_address=lead.property_address,
        property_normalized=normalize_entity(
            f"{lead.property_address} {lead.city} {lead.state}"
        ),
        market=market,
        market_normalized=normalize_entity(market),
        trigger=enrichment.recent_trigger,
        trigger_normalized=normalize_entity(enrichment.recent_trigger),
        source_fact_ids=source_ids,
        source_categories=dedupe(
            normalize_entity(source.source or source.label)
            for source in enrichment.sources
            if normalize_entity(source.source or source.label)
        ),
    )


def project_lead_graph(
    *,
    lead_id: str,
    lead: LeadCreate,
    enrichment: Enrichment,
    graph_context: KnowledgeGraphContext,
) -> LeadKnowledgeGraph:
    record = build_lead_graph_record(
        lead_id=lead_id,
        lead=lead,
        enrichment=enrichment,
    )
    lead_node_id = f"lead:{lead_id}"
    contact_id = graph_node_id("contact", f"{lead.contact_name} {lead.company}")
    company_id = graph_node_id("company", lead.company)
    property_id = graph_node_id(
        "property",
        f"{lead.property_address} {lead.city} {lead.state}",
    )
    market_id = graph_node_id("market", record.market)
    nodes = [
        KnowledgeGraphNode(
            id=lead_node_id,
            kind="lead",
            label=lead.contact_name,
            subtitle="Current inbound lead",
        ),
        KnowledgeGraphNode(
            id=contact_id,
            kind="contact",
            label=lead.contact_name,
            subtitle=lead.role,
        ),
        KnowledgeGraphNode(
            id=company_id,
            kind="company",
            label=lead.company,
            subtitle="Submitted company",
        ),
        KnowledgeGraphNode(
            id=property_id,
            kind="property",
            label=lead.property_address,
            subtitle=f"{lead.city}, {lead.state}",
        ),
        KnowledgeGraphNode(
            id=market_id,
            kind="market",
            label=record.market,
            subtitle="Resolved market",
        ),
    ]
    edges = [
        _edge(
            lead_node_id,
            contact_id,
            "HAS_CONTACT",
            "Lead input includes this contact.",
            1.0,
        ),
        _edge(
            contact_id,
            company_id,
            "WORKS_AT",
            "Lead input maps contact to submitted company.",
            0.9,
        ),
        _edge(
            lead_node_id,
            property_id,
            "ABOUT_PROPERTY",
            "Lead input includes this property context.",
            1.0,
        ),
        _edge(
            property_id,
            market_id,
            "IN_MARKET",
            "Enrichment resolved the property's market.",
            0.9,
        ),
    ]
    source_nodes, source_edges, sources = _source_fact_graph(
        lead_node_id=lead_node_id,
        enrichment=enrichment,
    )
    nodes.extend(source_nodes)
    edges.extend(source_edges)
    if enrichment.recent_trigger:
        trigger_id = graph_node_id("trigger", enrichment.recent_trigger)
        trigger_source_ids = [
            source.id
            for source in sources
            if "trigger" in normalize_entity(f"{source.label} {source.value}")
        ]
        nodes.append(
            KnowledgeGraphNode(
                id=trigger_id,
                kind="trigger",
                label=enrichment.recent_trigger,
                subtitle="Recent trigger",
                source_fact_ids=trigger_source_ids,
            )
        )
        edges.append(
            _edge(
                company_id,
                trigger_id,
                "HAS_TRIGGER",
                "Enrichment found a recent company trigger.",
                0.8,
                trigger_source_ids,
            )
        )
    for related in graph_context.related_leads:
        related_node_id = f"lead:{related.lead_id}"
        nodes.append(
            KnowledgeGraphNode(
                id=related_node_id,
                kind="lead",
                label=related.label,
                subtitle="Related inbound lead",
                source_fact_ids=related.source_fact_ids,
            )
        )
        edges.append(
            _edge(
                lead_node_id,
                related_node_id,
                "RELATED_TO",
                related.reason,
                related.confidence,
                related.source_fact_ids,
            )
        )
    return LeadKnowledgeGraph(
        nodes=_dedupe_nodes(nodes),
        edges=_dedupe_edges(edges),
        sources=sources,
        related_leads=graph_context.related_leads,
        warnings=graph_context.warnings,
    )


def related_leads_for_record(
    record: KnowledgeGraphLeadRecord,
    candidates: Iterable[KnowledgeGraphRelatedCandidate],
) -> list[KnowledgeGraphRelatedLead]:
    related: dict[str, KnowledgeGraphRelatedLead] = {}
    for candidate in candidates:
        if candidate.lead_id == record.lead_id:
            continue
        relation = _relation_for_candidate(record, candidate)
        if relation is None:
            continue
        current = related.get(relation.lead_id)
        if current is None or relation.confidence > current.confidence:
            related[relation.lead_id] = relation
    return sorted(
        related.values(),
        key=lambda item: (-item.confidence, item.label, item.lead_id),
    )[:5]


def graph_talking_points(related: Iterable[KnowledgeGraphRelatedLead]) -> list[str]:
    points = []
    for item in related:
        if item.source_fact_ids:
            points.append(f"Related inbound signal for prioritization: {item.reason}")
    return dedupe(points)


def dedupe(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _relation_for_candidate(
    record: KnowledgeGraphLeadRecord,
    candidate: KnowledgeGraphRelatedCandidate,
) -> KnowledgeGraphRelatedLead | None:
    shared_source_ids = _shared(record.source_fact_ids, candidate.source_fact_ids)
    if (
        candidate.company_normalized
        and candidate.company_normalized == record.company_normalized
    ):
        return KnowledgeGraphRelatedLead(
            lead_id=candidate.lead_id,
            label=candidate.label,
            reason="Same normalized company.",
            confidence=0.95,
            source_fact_ids=shared_source_ids,
        )
    if (
        candidate.market_normalized
        and candidate.market_normalized == record.market_normalized
    ):
        similar_context = candidate.property_normalized == record.property_normalized
        similar_context = similar_context or _token_overlap(
            record.company_normalized,
            candidate.company_normalized,
        )
        return KnowledgeGraphRelatedLead(
            lead_id=candidate.lead_id,
            label=candidate.label,
            reason=(
                "Same market with similar company or property context."
                if similar_context
                else "Same market context."
            ),
            confidence=0.65 if similar_context else 0.5,
            source_fact_ids=shared_source_ids,
        )
    if (
        record.trigger_normalized
        and candidate.trigger_normalized
        and candidate.trigger_normalized == record.trigger_normalized
    ):
        return KnowledgeGraphRelatedLead(
            lead_id=candidate.lead_id,
            label=candidate.label,
            reason="Shared trigger context.",
            confidence=0.6,
            source_fact_ids=shared_source_ids,
        )
    shared_categories = _shared(record.source_categories, candidate.source_categories)
    if shared_categories:
        return KnowledgeGraphRelatedLead(
            lead_id=candidate.lead_id,
            label=candidate.label,
            reason="Shared source category.",
            confidence=0.4,
            source_fact_ids=shared_source_ids,
        )
    return None


def _source_fact_graph(
    *,
    lead_node_id: str,
    enrichment: Enrichment,
) -> tuple[
    list[KnowledgeGraphNode],
    list[KnowledgeGraphEdge],
    list[KnowledgeGraphSource],
]:
    nodes: list[KnowledgeGraphNode] = []
    edges: list[KnowledgeGraphEdge] = []
    sources: list[KnowledgeGraphSource] = []
    for source_fact in enrichment.sources:
        source_id = _source_id(source_fact)
        sources.append(
            KnowledgeGraphSource(
                id=source_id,
                source=source_fact.source,
                label=source_fact.label,
                value=source_fact.value,
                url=source_fact.url,
            )
        )
        nodes.append(
            KnowledgeGraphNode(
                id=source_id,
                kind="source_fact",
                label=source_fact.label,
                subtitle=source_fact.source,
                source_fact_ids=[source_id],
            )
        )
        edges.append(
            _edge(
                lead_node_id,
                source_id,
                "HAS_SOURCE_FACT",
                "Enrichment attached this citable source fact.",
                1.0,
                [source_id],
            )
        )
    return nodes, edges, sources


def _edge(
    source: str,
    target: str,
    relationship: str,
    reason: str,
    confidence: float,
    source_fact_ids: list[str] | None = None,
) -> KnowledgeGraphEdge:
    return KnowledgeGraphEdge(
        id=f"{source}:{relationship}:{target}",
        source=source,
        target=target,
        relationship=relationship,  # type: ignore[arg-type]
        reason=reason,
        confidence=confidence,
        source_fact_ids=source_fact_ids or [],
    )


def _source_id(source_fact) -> str:
    source_key = (
        f"{source_fact.source} {source_fact.label} "
        f"{source_fact.value} {source_fact.url or ''}"
    )
    return graph_node_id(
        "source_fact",
        source_key,
    )


def _dedupe_nodes(nodes: Iterable[KnowledgeGraphNode]) -> list[KnowledgeGraphNode]:
    return list({node.id: node for node in nodes}.values())


def _dedupe_edges(edges: Iterable[KnowledgeGraphEdge]) -> list[KnowledgeGraphEdge]:
    return list({edge.id: edge for edge in edges}.values())


def _disabled_warnings(storage_enabled: bool) -> list[str]:
    if storage_enabled:
        return []
    return ["knowledge graph storage disabled; returned current lead graph only"]


def _shared(left: Iterable[str], right: Iterable[str]) -> list[str]:
    right_set = set(right)
    return [value for value in left if value in right_set]


def _token_overlap(left: str, right: str | None) -> bool:
    if not right:
        return False
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    if not left_tokens or not right_tokens:
        return False
    overlap = len(left_tokens & right_tokens)
    return overlap / max(len(left_tokens), len(right_tokens)) >= 0.5
