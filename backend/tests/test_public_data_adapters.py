import pytest

from app.integrations.public_data import PublicDataClient, PublicDataClientConfig
from app.schemas.lead import LeadCreate


def _lead(**overrides: object) -> LeadCreate:
    values = {
        "contact_name": "Demo Contact",
        "email": "contact@operator.example",
        "company": "Regional Property Operator",
        "role": "VP Leasing",
        "property_address": "123 Market St",
        "city": "Austin",
        "state": "TX",
        "country": "US",
    }
    values.update(overrides)
    return LeadCreate(**values)


@pytest.mark.asyncio
async def test_public_data_client_normalizes_successful_fixture_facts() -> None:
    client = PublicDataClient(PublicDataClientConfig(use_fixtures=True))

    result = await client.enrich(_lead())

    assert result.enrichment.market == "Austin, TX"
    assert result.enrichment.coordinates is not None
    assert result.enrichment.geo_confidence == "high"
    assert result.enrichment.domain_status == "corporate"
    assert result.enrichment.company_units == 85000
    assert result.warnings == []
    assert result.degraded_reasons == []
    fact_labels = {fact.label for fact in result.enrichment.sources}
    assert fact_labels >= {
        "Address resolution",
        "Renter share",
        "Rent growth",
        "Company units",
        "Domain quality",
    }
    assert all(fact.value for fact in result.enrichment.sources)


@pytest.mark.asyncio
async def test_public_data_client_marks_optional_no_data_as_degraded() -> None:
    client = PublicDataClient(PublicDataClientConfig(use_fixtures=True))

    result = await client.enrich(_lead(city="Raleigh", state="NC"))

    assert result.enrichment.market == "Raleigh, NC"
    assert result.enrichment.coordinates is not None
    assert result.enrichment.recent_trigger is None
    assert result.enrichment.walkability_score is None
    assert "local context unavailable" in result.warnings
    assert "trigger context unavailable" in result.warnings
    assert result.degraded_reasons == [
        "local_context: fixture no-data",
        "trigger_context: fixture no-data",
    ]
    assert any(
        fact.label == "Trigger event" and fact.confidence == "fallback"
        for fact in result.enrichment.sources
    )


@pytest.mark.asyncio
async def test_public_data_client_flags_personal_domain_quality() -> None:
    client = PublicDataClient(PublicDataClientConfig(use_fixtures=True))

    result = await client.enrich(_lead(email="contact@gmail.com"))

    assert result.enrichment.domain_status == "personal"
    assert any(
        fact.label == "Domain quality" and fact.value == "personal"
        for fact in result.enrichment.sources
    )
