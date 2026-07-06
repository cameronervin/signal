import pytest

from app.repositories.memory import InMemorySignalRepository
from app.schemas.lead import LeadCreate
from app.services.lead_service import LeadService


@pytest.mark.asyncio
async def test_pipeline_scores_and_drafts_gate_passed_lead() -> None:
    service = LeadService(InMemorySignalRepository())
    lead = LeadCreate(
        contact_name="Sarah Chen",
        email="sarah@meridianresidential.example",
        company="Meridian Residential",
        role="VP Leasing",
        property_address="123 Market St",
        city="Austin",
        state="TX",
        country="US",
    )

    result = await service.create_and_enrich(lead)

    assert result.gates.status == "passed"
    assert result.score.tier == "A"
    assert result.draft is not None
    assert result.score.why_line
    assert result.related_leads


@pytest.mark.asyncio
async def test_pipeline_suppresses_draft_for_gate_failed_lead() -> None:
    service = LeadService(InMemorySignalRepository())
    lead = LeadCreate(
        contact_name="Tom Whitaker",
        email="tom@gmail.com",
        company="Unverified Homes",
        role="Property Manager",
        property_address="500 Ocean Dr",
        city="Miami",
        state="FL",
        country="US",
    )

    result = await service.create_and_enrich(lead)

    assert result.gates.status == "failed"
    assert result.score.tier == "C"
    assert result.draft is None
    assert "personal email domain" in result.flags
