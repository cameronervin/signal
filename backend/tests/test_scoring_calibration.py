import pytest

from app.agents.fixtures import demo_enrichment
from app.agents.scoring import evaluate_gates, score_lead
from app.repositories.memory import InMemorySignalRepository
from app.schemas.lead import LeadCreate, ScoreBreakdown
from app.services.lead_service import LeadService


def _component_points(lead) -> dict[str, int]:
    return {component.name: component.points for component in lead.score.components}


def _score_component_points(score: ScoreBreakdown) -> dict[str, int]:
    return {component.name: component.points for component in score.components}


def _source_labels(lead) -> set[str]:
    return {source.label for source in lead.enrichment.sources}


@pytest.mark.asyncio
async def test_demo_fixture_scores_match_documented_calibration() -> None:
    service = LeadService(InMemorySignalRepository())

    await service.seed_demo_leads()
    leads = {lead.id.removeprefix("seed_"): lead for lead in await service.list_leads()}

    assert {
        handle: (
            lead.score.tier,
            lead.score.company_fit,
            lead.score.market_opportunity,
            lead.score.total,
        )
        for handle, lead in leads.items()
    } == {
        "a_tier": ("A", 60, 40, 100),
        "b_tier": ("B", 42, 27, 69),
        "c_tier": ("C", 24, 9, 33),
        "warning_only": ("B", 32, 40, 72),
        "missing_trigger": ("B", 32, 27, 59),
        "hard_gate_failed": ("C", 0, 0, 0),
    }

    assert _component_points(leads["a_tier"]) == {
        "portfolio_scale": 25,
        "contact_seniority": 15,
        "asset_type_fit": 10,
        "company_momentum": 10,
        "renter_share": 12,
        "rent_level_trend": 10,
        "population_household_growth": 8,
        "labor_market_tightness": 5,
        "walkability_density": 5,
        "recent_trigger_bonus": 10,
        "related_context_bonus": 0,
    }
    assert _component_points(leads["b_tier"]) == {
        "portfolio_scale": 21,
        "contact_seniority": 7,
        "asset_type_fit": 10,
        "company_momentum": 4,
        "renter_share": 6,
        "rent_level_trend": 5,
        "population_household_growth": 8,
        "labor_market_tightness": 5,
        "walkability_density": 3,
        "recent_trigger_bonus": 0,
        "related_context_bonus": 0,
    }
    assert _component_points(leads["c_tier"])["portfolio_scale"] == 6
    assert _component_points(leads["c_tier"])["renter_share"] == 3
    assert leads["warning_only"].gates.warnings == ["sub-scale portfolio"]
    assert leads["warning_only"].draft is not None
    assert leads["missing_trigger"].enrichment.recent_trigger is None
    assert leads["missing_trigger"].draft is not None
    assert leads["hard_gate_failed"].draft is None

    for handle, lead in leads.items():
        assert lead.score.why_line.startswith(f"{lead.score.tier}-tier:")
        assert lead.score.why_line
        if handle == "hard_gate_failed":
            assert "non-US property" in lead.score.why_line
            continue
        source_labels = _source_labels(lead)
        assert source_labels
        for component in lead.score.components:
            assert set(component.source_refs).issubset(source_labels)
            assert component.rationale


def test_bonus_points_are_bounded_and_total_score_is_capped() -> None:
    lead = LeadCreate(
        contact_name="Demo Contact",
        email="contact@operator.example",
        company="National Property Operator",
        role="Chief Revenue Officer",
        property_address="100 Market St",
        city="Austin",
        state="TX",
        country="US",
    )
    enrichment = demo_enrichment(lead.company, lead.city, lead.state)
    gates = evaluate_gates(lead, enrichment)

    score = score_lead(
        lead,
        gates,
        enrichment,
        related_context_count=4,
    )

    assert score.company_fit == 60
    assert score.market_opportunity == 40
    assert score.total == 100
    assert _score_component_points(score)["recent_trigger_bonus"] == 10
    assert _score_component_points(score)["related_context_bonus"] == 10
    assert score.multipliers == ["recent_trigger:+10", "related_context:+10"]


@pytest.mark.asyncio
async def test_hard_gate_failure_forces_c_tier_and_suppresses_draft() -> None:
    service = LeadService(InMemorySignalRepository())
    lead = LeadCreate(
        contact_name="Demo Contact",
        email="contact@gmail.com",
        company="National Property Operator",
        role="Chief Revenue Officer",
        property_address="100 Market St",
        city="Austin",
        state="TX",
        country="US",
    )

    result = await service.create_and_enrich(lead)

    assert result.gates.status == "failed"
    assert result.gates.failures == ["personal email domain"]
    assert result.score.tier == "C"
    assert result.score.total == 0
    assert result.score.company_fit == 0
    assert result.score.market_opportunity == 0
    assert result.draft is None
