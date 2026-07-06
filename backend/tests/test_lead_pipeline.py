import pytest
from pydantic import ValidationError

from app.repositories.memory import InMemorySignalRepository
from app.schemas.lead import LeadCreate
from app.services.lead_service import LeadService


@pytest.mark.asyncio
async def test_pipeline_returns_fresh_contract_for_gate_passed_lead() -> None:
    service = LeadService(InMemorySignalRepository())
    lead = LeadCreate.model_validate(
        {
            "contact_name": "Demo Contact",
            "email": "contact@operator.example",
            "company": "Regional Residential",
            "role": "VP Leasing",
            "source": "web_form",
            "submitted_at": "2026-07-06T12:00:00Z",
            "property_address": "123 Market St",
            "city": "Austin",
            "state": "TX",
            "country": "US",
            "score": {"total": 100, "tier": "A"},
            "draft": {"subject": "Untrusted", "body": "Untrusted"},
        }
    )

    result = await service.create_and_enrich(lead)

    assert result.gates.status == "passed"
    assert result.score.tier == "A"
    assert result.draft is not None
    assert result.draft_state.eligible is True
    assert result.draft_state.status == "awaiting_review"
    assert result.review_state.status == "awaiting_review"
    assert result.review_state.human_review_required is True
    assert result.input.source == "web_form"
    assert result.input.submitted_at is not None
    assert not hasattr(result.input, "score")
    assert result.source_facts == result.enrichment.sources
    assert result.score.why_line
    assert result.related_context
    assert result.draft.subject != "Untrusted"


@pytest.mark.asyncio
async def test_pipeline_returns_gate_failed_contract_without_draft() -> None:
    service = LeadService(InMemorySignalRepository())
    lead = LeadCreate(
        contact_name="Demo Manager",
        email="manager@personal.example",
        company="Local Homes",
        role="Property Manager",
        source="manual_entry",
        submitted_at="2026-07-06T12:05:00Z",
        property_address="500 Ocean Dr",
        city="Miami",
        state="FL",
        country="US",
    )

    result = await service.create_and_enrich(lead)

    assert result.gates.status == "failed"
    assert result.score.tier == "C"
    assert result.draft is None
    assert result.draft_state.eligible is False
    assert result.draft_state.status == "blocked"
    assert result.draft_state.reason == "personal email domain"
    assert result.review_state.status == "blocked"
    assert result.review_state.reason == "personal email domain"
    assert "personal email domain" in result.flags


@pytest.mark.asyncio
async def test_repository_persists_updated_lead_and_run_contracts() -> None:
    repository = InMemorySignalRepository()
    service = LeadService(repository)
    passed = await service.create_and_enrich(
        LeadCreate(
            contact_name="Demo Contact",
            email="contact@operator.example",
            company="Regional Residential",
            role="VP Leasing",
            property_address="123 Market St",
            city="Austin",
            state="TX",
            country="US",
        )
    )
    failed = await service.create_and_enrich(
        LeadCreate(
            contact_name="Demo Manager",
            email="manager@personal.example",
            company="Local Homes",
            role="Property Manager",
            property_address="500 Ocean Dr",
            city="Miami",
            state="FL",
            country="US",
        )
    )

    leads = await repository.list_leads()
    runs = await repository.list_agent_runs()
    failed_run = await repository.get_agent_run(failed.run_id)

    assert [lead.id for lead in leads] == [passed.id, failed.id]
    assert {run.run_id for run in runs} == {passed.run_id, failed.run_id}
    assert failed_run is not None
    assert failed_run.current_stage == "gate_failed"
    assert failed_run.stage_index == 3
    assert failed_run.degraded_reasons == ["personal email domain"]
    assert all("@" not in entry for entry in failed_run.activity_log)


def test_lead_input_rejects_invalid_email_and_required_location_fields() -> None:
    with pytest.raises(ValidationError) as validation_error:
        LeadCreate.model_validate(
            {
                "contact_name": "Demo Contact",
                "email": "not-an-email",
                "company": "Regional Residential",
                "property_address": "   ",
                "city": "",
                "state": "",
                "country": "",
            }
        )

    error_fields = {tuple(error["loc"]) for error in validation_error.value.errors()}
    assert ("email",) in error_fields
    assert ("property_address",) in error_fields
    assert ("city",) in error_fields
    assert ("state",) in error_fields
    assert ("country",) in error_fields
