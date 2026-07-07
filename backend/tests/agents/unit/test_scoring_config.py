from app.agents.utils.scoring import (
    clear_scoring_config_cache,
    load_scoring_config,
    score_lead,
)
from app.core.config import Settings
from app.infrastructure.public_data.fixtures import demo_enrichment
from app.schemas.lead import GateResult, LeadCreate


def _lead() -> LeadCreate:
    return LeadCreate(
        contact_name="Sample Contact",
        email="lead@sampleoperator.example",
        company="Sample Residential Group",
        role="VP Leasing",
        property_address="100 Main St",
        city="Austin",
        state="TX",
        country="US",
    )


def test_default_scoring_config_preserves_existing_score_behavior() -> None:
    lead = _lead()
    score = score_lead(
        lead,
        GateResult(status="passed"),
        demo_enrichment(
            lead.company,
            lead.city,
            lead.state,
        ),
    )

    assert score.total == 100
    assert score.tier == "A"


def test_scoring_config_can_load_from_settings_path(tmp_path) -> None:
    config_path = tmp_path / "scoring.json"
    config_path.write_text('{"tier_a_min": 101}')
    clear_scoring_config_cache()

    config = load_scoring_config(Settings(scoring_config_path=str(config_path)))
    lead = _lead()
    score = score_lead(
        lead,
        GateResult(status="passed"),
        demo_enrichment(lead.company, lead.city, lead.state),
        config=config,
    )

    assert score.total == 100
    assert score.tier == "B"
    clear_scoring_config_cache()


def test_empty_scoring_config_path_uses_defaults() -> None:
    clear_scoring_config_cache()

    config = load_scoring_config(Settings(scoring_config_path=""))

    assert config.tier_a_min == 75
    clear_scoring_config_cache()
