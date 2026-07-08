from app.agents.utils.talking_points import talking_points_for_enrichment
from app.schemas.knowledge_graph import KnowledgeGraphRelatedLead
from app.schemas.lead import Enrichment
from app.services.knowledge_graph_service import graph_talking_points


def test_talking_points_are_use_case_anchored_sales_insights() -> None:
    points = talking_points_for_enrichment(
        Enrichment(
            market="Austin, TX",
            renter_share=0.64,
            rent_growth_yoy=6.2,
            company_units=42000,
        )
    )

    assert points == [
        (
            "Austin, TX has 64% renter share, a demand signal for leasing "
            "volume and prospect follow-up."
        ),
        (
            "Local rent growth is 6.2% year over year, which can make "
            "response speed and tour conversion more urgent."
        ),
        (
            "Portfolio scale signal: about 42,000 units, suggesting follow-up "
            "complexity and team-capacity pressure."
        ),
    ]
    assert "ROI" not in " ".join(points)


def test_graph_talking_points_anchor_related_context_to_prioritization() -> None:
    points = graph_talking_points(
        [
            KnowledgeGraphRelatedLead(
                lead_id="lead_123",
                label="Related inbound",
                reason="Same market and trigger.",
                confidence=0.8,
                source_fact_ids=["source_1"],
            ),
            KnowledgeGraphRelatedLead(
                lead_id="lead_456",
                label="Uncited related inbound",
                reason="Same market.",
                confidence=0.5,
            ),
        ]
    )

    assert points == [
        "Related inbound signal for prioritization: Same market and trigger."
    ]


def test_graph_talking_points_deduplicate_repeated_related_reasons() -> None:
    points = graph_talking_points(
        [
            KnowledgeGraphRelatedLead(
                lead_id="lead_123",
                label="Related inbound",
                reason="Shared source category.",
                confidence=0.4,
                source_fact_ids=["source_1"],
            ),
            KnowledgeGraphRelatedLead(
                lead_id="lead_456",
                label="Related inbound",
                reason="Shared source category.",
                confidence=0.4,
                source_fact_ids=["source_2"],
            ),
        ]
    )

    assert points == [
        "Related inbound signal for prioritization: Shared source category."
    ]
