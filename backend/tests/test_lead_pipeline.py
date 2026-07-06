import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.repositories.memory import InMemorySignalRepository
from app.schemas.lead import LeadCreate
from app.services.lead_service import LeadService, get_lead_service


@pytest.mark.asyncio
async def test_pipeline_scores_and_drafts_gate_passed_lead() -> None:
    repository = InMemorySignalRepository()
    service = LeadService(repository)
    lead = LeadCreate(
        contact_name="Demo Contact",
        email="contact@operator.example",
        company="Regional Property Operator",
        role="VP Leasing",
        property_address="123 Market St",
        city="Austin",
        state="TX",
        country="US",
        source="demo_request",
    )

    result = await service.create_and_enrich(lead)
    stored_run = await repository.get_agent_run(result.run_id)

    assert result.input.source == "demo_request"
    assert result.input.submitted_at is not None
    assert result.gates.status == "passed"
    assert result.enrichment.geo_confidence == "high"
    assert result.enrichment.census_geo_id
    assert result.enrichment.walkability_score is not None
    assert result.enrichment.asset_type_fit == "multifamily"
    assert result.enrichment.domain_status == "corporate"
    assert result.enrichment.sources
    assert result.enrichment.sources[0].retrieved_at is not None
    assert result.enrichment.sources[0].confidence == "high"
    assert {source.label for source in result.enrichment.sources} >= {"Company units"}
    assert result.score.tier == "A"
    assert result.score.components
    assert result.score.components[0].name == "portfolio_scale"
    assert result.score.components[0].rationale
    assert result.score.multipliers
    assert result.draft is not None
    assert result.draft.generation_mode == "fallback_template"
    assert result.draft.review_status == "needs_review"
    assert result.draft.talking_points
    assert result.score.why_line
    assert result.related_leads
    assert result.related_leads[0].relationship_type == "company"
    assert stored_run is not None
    assert stored_run.run_id == result.run_id
    assert stored_run.execution_mode == "inline"
    assert stored_run.task_id is None
    assert stored_run.worker_queue is None
    assert stored_run.degraded_reasons == []
    assert stored_run.steps[0].stage == "deterministic_enrichment"
    assert "api_insert: lead received" in stored_run.activity_log
    assert all("@" not in entry for entry in stored_run.activity_log)


@pytest.mark.asyncio
async def test_repository_lists_updated_lead_and_run_structures() -> None:
    repository = InMemorySignalRepository()
    service = LeadService(repository)
    lead = LeadCreate(
        contact_name="Demo Contact",
        email="contact@operator.example",
        company="Regional Property Operator",
        role="VP Leasing",
        property_address="123 Market St",
        city="Austin",
        state="TX",
        country="US",
    )

    result = await service.create_and_enrich(lead)

    assert await repository.list_leads() == [result]
    runs = await repository.list_agent_runs()
    assert len(runs) == 1
    assert runs[0].lead_id == result.id
    assert runs[0].current_stage == "human_review"


@pytest.mark.asyncio
async def test_pipeline_suppresses_draft_for_gate_failed_lead() -> None:
    service = LeadService(InMemorySignalRepository())
    lead = LeadCreate(
        contact_name="Demo Contact",
        email="contact@operator.example",
        company="Unverified Housing",
        role="Property Manager",
        property_address="500 Ocean Dr",
        city="Toronto",
        state="ON",
        country="CA",
    )

    result = await service.create_and_enrich(lead)

    assert result.gates.status == "failed"
    assert result.score.tier == "C"
    assert result.draft is None
    assert "non-US property" in result.flags
    assert result.score.components[0].name == "gates"


@pytest.mark.asyncio
async def test_pipeline_allows_draft_when_optional_adapters_degrade() -> None:
    repository = InMemorySignalRepository()
    service = LeadService(repository)
    lead = LeadCreate(
        contact_name="Demo Contact",
        email="contact@operator.example",
        company="Regional Property Operator",
        role="Director of Leasing",
        property_address="123 Market St",
        city="Raleigh",
        state="NC",
        country="US",
    )

    result = await service.create_and_enrich(lead)
    stored_run = await repository.get_agent_run(result.run_id)

    assert result.gates.status == "passed"
    assert result.draft is not None
    assert "local context unavailable" in result.flags
    assert "trigger context unavailable" in result.flags
    assert stored_run is not None
    assert stored_run.degraded_reasons == [
        "local_context: fixture no-data",
        "trigger_context: fixture no-data",
    ]


@pytest.mark.asyncio
async def test_pipeline_gate_fails_for_unverified_company_and_domain() -> None:
    service = LeadService(InMemorySignalRepository())
    lead = LeadCreate(
        contact_name="Demo Contact",
        email="contact@gmail.com",
        company="Unverified Consulting",
        role="Property Manager",
        property_address="123 Market St",
        city="Austin",
        state="TX",
        country="US",
    )

    result = await service.create_and_enrich(lead)

    assert result.gates.status == "failed"
    assert result.score.tier == "C"
    assert result.draft is None
    assert "corporate domain not verified" in result.gates.failures
    assert "company plausibility unresolved" in result.gates.failures


@pytest.mark.asyncio
async def test_create_lead_accepts_fresh_input_contract() -> None:
    app = create_app()
    repository = InMemorySignalRepository()

    async def override_service() -> LeadService:
        return LeadService(repository)

    app.dependency_overrides[get_lead_service] = override_service

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/leads",
            json={
                "contact_name": "Demo Contact",
                "email": "contact@operator.example",
                "company": "Regional Property Operator",
                "role": "VP Leasing",
                "property_address": "123 Market St",
                "city": "Austin",
                "state": "TX",
                "country": "US",
                "source": "demo_request",
                "submitted_at": "2026-01-15T13:30:00Z",
            },
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["input"]["source"] == "demo_request"
    assert payload["input"]["submitted_at"] == "2026-01-15T13:30:00Z"
    assert payload["run_id"].startswith("run_")
    assert payload["draft"]["review_status"] == "needs_review"
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_lead_rejects_invalid_email_and_missing_location_fields() -> None:
    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/leads",
            json={
                "contact_name": "Demo Contact",
                "email": "not-an-email",
                "company": "Regional Property Operator",
                "property_address": "",
                "city": "",
                "state": "TX",
                "country": "US",
            },
        )

    assert response.status_code == 422
    error_fields = {tuple(error["loc"]) for error in response.json()["detail"]}
    assert ("body", "email") in error_fields
    assert ("body", "property_address") in error_fields
    assert ("body", "city") in error_fields
