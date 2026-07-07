import pytest

from app.agents.executors.signal_pipeline import SignalPipelineExecutor
from app.schemas.lead import LeadCreate
from app.services.lead_service import LeadService
from tests.fakes import FakePublicDataClient, FakeSignalRepository


@pytest.mark.asyncio
async def test_pipeline_scores_and_drafts_gate_passed_lead() -> None:
    public_data_client = FakePublicDataClient()
    service = LeadService(
        FakeSignalRepository(),
        pipeline_executor=SignalPipelineExecutor(
            public_data_client=public_data_client,
        ),
    )
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
    assert "Public market data" in result.draft.body
    assert {source.label for source in result.draft.sources} == {
        "Renter share",
        "Rent growth",
        "Trigger event",
    }
    assert result.score.why_line
    assert result.related_leads
    assert public_data_client.calls == 1


@pytest.mark.asyncio
async def test_pipeline_suppresses_draft_for_gate_failed_lead() -> None:
    service = LeadService(
        FakeSignalRepository(),
        pipeline_executor=SignalPipelineExecutor(
            public_data_client=FakePublicDataClient(),
        ),
    )
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


@pytest.mark.asyncio
async def test_pipeline_marks_model_failure_without_fallback_draft(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def failing_acompletion(**kwargs):
        raise RuntimeError("model unavailable")

    monkeypatch.setattr("litellm.acompletion", failing_acompletion)
    service = LeadService(
        FakeSignalRepository(),
        pipeline_executor=SignalPipelineExecutor(
            public_data_client=FakePublicDataClient(),
        ),
    )
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
    runs = await service.list_agent_runs()

    assert result.gates.status == "passed"
    assert result.draft is None
    assert "model drafting failed" in result.flags
    assert runs[0].status == "failed"
    assert runs[0].current_stage == "model_drafting_failed"


@pytest.mark.asyncio
async def test_gate_failed_lead_never_calls_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    async def counted_acompletion(**kwargs):
        nonlocal calls
        calls += 1
        raise AssertionError("gate-failed lead should not call LiteLLM")

    monkeypatch.setattr("litellm.acompletion", counted_acompletion)
    service = LeadService(
        FakeSignalRepository(),
        pipeline_executor=SignalPipelineExecutor(
            public_data_client=FakePublicDataClient(),
        ),
    )
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
    assert result.draft is None
    assert calls == 0
