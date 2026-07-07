import pytest

from app.infrastructure.knowledge_graph.repositories import (
    DisabledKnowledgeGraphRepository,
)
from app.schemas.knowledge_graph import KnowledgeGraphRelatedCandidate
from app.schemas.lead import Enrichment, LeadCreate, SourceFact
from app.services.knowledge_graph_service import (
    KnowledgeGraphService,
    build_lead_graph_record,
    graph_node_id,
    normalize_entity,
    related_leads_for_record,
)


def test_entity_normalization_and_graph_ids_are_deterministic() -> None:
    assert normalize_entity("  Example,  Homes LLC  ") == "example homes llc"
    assert graph_node_id("company", "Example Homes") == graph_node_id(
        "company",
        " example--homes ",
    )


def test_current_lead_projection_includes_core_nodes_and_edges() -> None:
    service = KnowledgeGraphService(
        DisabledKnowledgeGraphRepository(),
        storage_enabled=False,
    )

    graph = service.project_lead_graph(
        lead_id="lead_current",
        lead=_lead(),
        enrichment=_enrichment(),
    )

    assert {node.kind for node in graph.nodes} == {
        "lead",
        "contact",
        "company",
        "property",
        "market",
        "source_fact",
        "trigger",
    }
    assert {
        "HAS_CONTACT",
        "WORKS_AT",
        "ABOUT_PROPERTY",
        "IN_MARKET",
        "HAS_SOURCE_FACT",
        "HAS_TRIGGER",
    }.issubset({edge.relationship for edge in graph.edges})
    assert graph.sources


def test_same_company_lead_produces_high_confidence_relation() -> None:
    record = build_lead_graph_record(
        lead_id="lead_current",
        lead=_lead(),
        enrichment=_enrichment(),
    )

    related = related_leads_for_record(
        record,
        [
            KnowledgeGraphRelatedCandidate(
                lead_id="lead_previous",
                label="Previous Lead",
                company_normalized=record.company_normalized,
                market_normalized="other market",
            )
        ],
    )

    assert related[0].lead_id == "lead_previous"
    assert related[0].confidence == pytest.approx(0.95)
    assert related[0].reason == "Same normalized company."


def test_same_market_only_relation_is_bounded_medium_confidence() -> None:
    record = build_lead_graph_record(
        lead_id="lead_current",
        lead=_lead(),
        enrichment=_enrichment(),
    )

    related = related_leads_for_record(
        record,
        [
            KnowledgeGraphRelatedCandidate(
                lead_id="lead_market",
                label="Market Lead",
                company_normalized="different operator",
                property_normalized="different address",
                market_normalized=record.market_normalized,
            )
        ],
    )

    assert related[0].confidence == pytest.approx(0.5)
    assert related[0].reason == "Same market context."


def test_unrelated_leads_do_not_produce_edges() -> None:
    record = build_lead_graph_record(
        lead_id="lead_current",
        lead=_lead(),
        enrichment=_enrichment(),
    )

    related = related_leads_for_record(
        record,
        [
            KnowledgeGraphRelatedCandidate(
                lead_id="lead_unrelated",
                label="Unrelated Lead",
                company_normalized="different operator",
                market_normalized="different market",
                source_categories=["different source"],
            )
        ],
    )

    assert related == []


@pytest.mark.asyncio
async def test_disabled_mode_returns_current_projection_with_warning() -> None:
    service = KnowledgeGraphService(
        DisabledKnowledgeGraphRepository(),
        storage_enabled=False,
    )
    lead = _lead()
    enrichment = _enrichment()

    context = await service.ingest_lead_graph(
        lead_id="lead_current",
        lead=lead,
        enrichment=enrichment,
    )
    graph_context = await service.retrieve_graph_context(
        lead_id="lead_current",
        lead=lead,
        enrichment=enrichment,
        existing_warnings=context.warnings,
    )
    graph = service.project_lead_graph(
        lead_id="lead_current",
        lead=lead,
        enrichment=enrichment,
        graph_context=graph_context,
    )

    assert graph.related_leads == []
    assert graph.warnings == [
        "knowledge graph storage disabled; returned current lead graph only"
    ]
    assert any(node.kind == "lead" for node in graph.nodes)


@pytest.mark.asyncio
async def test_repository_failure_surfaces_graph_warning() -> None:
    service = KnowledgeGraphService(
        FailingKnowledgeGraphRepository(),
        storage_enabled=True,
    )

    context = await service.retrieve_graph_context(
        lead_id="lead_current",
        lead=_lead(),
        enrichment=_enrichment(),
    )

    assert context.related_leads == []
    assert context.warnings == [
        "knowledge graph retrieval unavailable; returned current lead graph only"
    ]


class FailingKnowledgeGraphRepository:
    async def ingest_lead_graph(self, record, graph) -> None:
        raise RuntimeError("unavailable")

    async def find_related_leads(self, record):
        raise RuntimeError("unavailable")

    async def close(self) -> None:
        return None


def _lead() -> LeadCreate:
    return LeadCreate(
        contact_name="Sample Contact",
        email="sample@operator.example",
        company="Example Homes",
        role="VP Leasing",
        property_address="100 Main St",
        city="Austin",
        state="TX",
        country="US",
    )


def _enrichment() -> Enrichment:
    return Enrichment(
        market="Austin, TX",
        renter_share=0.61,
        median_rent=1840,
        rent_growth_yoy=8.1,
        household_growth=4.4,
        unemployment_rate=3.2,
        company_units=85000,
        recent_trigger="Example Homes announced portfolio expansion",
        sources=[
            SourceFact(
                source="Census ACS",
                label="Renter share",
                value="61%",
            ),
            SourceFact(
                source="News",
                label="Trigger event",
                value="Portfolio expansion",
            ),
        ],
    )
