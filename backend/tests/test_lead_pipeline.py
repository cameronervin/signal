import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.repositories.memory import InMemorySignalRepository
from app.schemas.lead import LeadCreate
from app.services.lead_service import LeadService, WorkerDispatch, get_lead_service


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
    assert result.run == stored_run
    assert stored_run.execution_mode == "inline"
    assert stored_run.task_id is None
    assert stored_run.worker_queue is None
    assert stored_run.degraded_reasons == []
    assert stored_run.steps[0].stage == "deterministic_enrichment"
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
    assert payload["run"]["run_id"] == payload["run_id"]
    assert payload["run"]["execution_mode"] == "inline"
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


@pytest.mark.asyncio
async def test_seed_demo_leads_resets_stable_fixture_set() -> None:
    repository = InMemorySignalRepository()
    service = LeadService(repository)
    transient = await service.create_and_enrich(
        LeadCreate(
            contact_name="Transient Contact",
            email="transient@operator.example",
            company="Regional Property Operator",
            role="VP Leasing",
            property_address="123 Market St",
            city="Austin",
            state="TX",
            country="US",
        )
    )

    first = await service.seed_demo_leads()
    second = await service.seed_demo_leads()

    handles = [seed.handle for seed in first.seeds]
    assert handles == [
        "a_tier",
        "b_tier",
        "c_tier",
        "warning_only",
        "missing_trigger",
        "hard_gate_failed",
    ]
    assert [seed.lead_id for seed in first.seeds] == [
        f"seed_{handle}" for handle in handles
    ]
    assert [seed.lead_id for seed in second.seeds] == [
        seed.lead_id for seed in first.seeds
    ]
    assert [seed.run_id for seed in second.seeds] == [
        seed.run_id for seed in first.seeds
    ]
    assert first.reset is True
    assert first.count == 6
    assert await repository.get_lead(transient.id) is None

    seeded_leads = await repository.list_leads()
    by_id = {lead.id: lead for lead in seeded_leads}
    assert len(seeded_leads) == 6
    assert by_id["seed_a_tier"].score.tier == "A"
    assert by_id["seed_b_tier"].score.tier == "B"
    assert by_id["seed_c_tier"].score.tier == "C"
    assert by_id["seed_warning_only"].gates.status == "passed"
    assert by_id["seed_warning_only"].gates.warnings
    assert by_id["seed_warning_only"].draft is not None
    assert by_id["seed_missing_trigger"].enrichment.recent_trigger is None
    assert by_id["seed_missing_trigger"].draft is not None
    assert by_id["seed_hard_gate_failed"].gates.status == "failed"
    assert by_id["seed_hard_gate_failed"].score.tier == "C"
    assert by_id["seed_hard_gate_failed"].draft is None


@pytest.mark.asyncio
async def test_seed_demo_leads_endpoint_returns_stable_run_handles() -> None:
    repository = InMemorySignalRepository()
    service = LeadService(repository)
    app = create_app(lead_service=service)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/api/v1/leads/seed")
        repeat = await client.post("/api/v1/leads/seed")

    assert response.status_code == 201
    assert repeat.status_code == 201
    payload = response.json()
    repeat_payload = repeat.json()
    assert payload["count"] == 6
    assert payload["seeds"] == repeat_payload["seeds"]
    assert payload["seeds"][0] == {
        "handle": "a_tier",
        "lead_id": "seed_a_tier",
        "run_id": "seed_run_a_tier",
        "tier": "A",
        "gate_status": "passed",
        "draft_available": True,
    }


class RecordingDispatcher:
    def __init__(self, repository: InMemorySignalRepository | None = None) -> None:
        self.calls: list[tuple[str, str, str]] = []
        self.repository = repository
        self.saved_before_dispatch = False

    async def dispatch_agent_run(self, *, lead_id: str, run_id: str) -> WorkerDispatch:
        self.calls.append((lead_id, run_id, "agent-runs"))
        if self.repository is not None:
            self.saved_before_dispatch = (
                await self.repository.get_lead(lead_id) is not None
                and await self.repository.get_agent_run(run_id) is not None
            )
        return WorkerDispatch(task_id=f"task_{run_id}", queue="agent-runs")


@pytest.mark.asyncio
async def test_worker_execution_mode_persists_queued_state_before_dispatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = InMemorySignalRepository()
    dispatcher = RecordingDispatcher(repository)
    service = LeadService(
        repository,
        execution_mode="worker",
        worker_dispatcher=dispatcher,
        worker_queue="agent-runs",
    )

    async def fail_inline_pipeline(_: object) -> object:
        raise AssertionError("worker dispatch must not run the pipeline inline")

    monkeypatch.setattr(
        "app.services.lead_service.run_signal_pipeline",
        fail_inline_pipeline,
    )
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
    stored_run = await repository.get_agent_run(result.run_id)

    assert dispatcher.calls == [(result.id, result.run_id, "agent-runs")]
    assert dispatcher.saved_before_dispatch is True
    assert stored_run is not None
    assert result.run == stored_run
    assert result.gates.status == "pending"
    assert result.score.why_line == "Agent run queued; score pending."
    assert result.draft is None
    assert stored_run.status == "queued"
    assert stored_run.execution_mode == "worker"
    assert stored_run.task_id == f"task_{result.run_id}"
    assert stored_run.worker_queue == "agent-runs"
    assert stored_run.activity_log[0] == "api_insert: lead received"
    assert stored_run.activity_log[-1] == "worker_dispatch: queued"
    assert all(step.status == "pending" for step in stored_run.steps)
    assert all("@" not in entry for entry in stored_run.activity_log)
