import json
from pathlib import Path

import pytest

from app.agents.fixtures import demo_enrichment
from app.agents.scoring import (
    evaluate_gates,
    load_default_scoring_rubric,
    score_lead,
)
from app.core.config import get_settings
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
        "b_tier": ("B", 42, 23, 65),
        "c_tier": ("C", 24, 23, 47),
        "warning_only": ("B", 32, 40, 72),
        "missing_trigger": ("B", 32, 23, 55),
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
        "related_context_bonus": 10,
    }
    assert _component_points(leads["b_tier"]) == {
        "portfolio_scale": 21,
        "contact_seniority": 7,
        "asset_type_fit": 10,
        "company_momentum": 4,
        "renter_share": 6,
        "rent_level_trend": 5,
        "population_household_growth": 6,
        "labor_market_tightness": 1,
        "walkability_density": 5,
        "recent_trigger_bonus": 0,
        "related_context_bonus": 0,
    }
    assert _component_points(leads["c_tier"])["portfolio_scale"] == 6
    assert _component_points(leads["c_tier"])["renter_share"] == 6
    assert leads["warning_only"].gates.warnings == ["trigger context unavailable"]
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


def test_scoring_config_path_loads_runtime_rubric(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    config = json.loads(Path("app/agents/scoring-rubric.v1.json").read_text())
    config["tier_thresholds"]["A"] = 101
    custom_config = tmp_path / "scoring-rubric.test.json"
    custom_config.write_text(json.dumps(config), encoding="utf-8")
    monkeypatch.setenv("SIGNAL_SCORING_CONFIG_PATH", str(custom_config))
    get_settings.cache_clear()
    load_default_scoring_rubric.cache_clear()

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
    score = score_lead(lead, evaluate_gates(lead, enrichment), enrichment)

    assert get_settings().scoring_config_path == str(custom_config)
    assert score.total == 100
    assert score.tier == "B"

    get_settings.cache_clear()
    load_default_scoring_rubric.cache_clear()


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
    assert result.gates.failures == ["corporate domain not verified"]
    assert result.score.tier == "C"
    assert result.score.total == 0
    assert result.score.company_fit == 0
    assert result.score.market_opportunity == 0
    assert result.draft is None


@pytest.mark.asyncio
async def test_client_source_cannot_claim_seeded_related_context() -> None:
    service = LeadService(InMemorySignalRepository())
    lead = LeadCreate(
        contact_name="Demo Contact",
        email="contact@operator.example",
        company="National Property Operator",
        role="VP Leasing",
        property_address="100 Market St",
        city="Austin",
        state="TX",
        country="US",
        source="demo_seed",
    )

    result = await service.create_and_enrich(lead)

    assert result.run is not None
    assert result.run.trigger == "api_insert"
    assert result.related_leads == []
    assert _component_points(result)["related_context_bonus"] == 0
    assert "related_context:+10" not in result.score.multipliers
