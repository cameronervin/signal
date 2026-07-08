import pytest

from app.agents.executors.signal_pipeline import SignalPipelineExecutor
from app.core.config import Settings
from app.schemas.lead import LeadCreate
from app.services.agent_execution_service import AgentExecutionService
from app.services.agent_run_service import AgentRunService
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.services.lead_intake_service import LeadIntakeService
from tests.fakes import FakePublicDataClient, FakeSignalRepository


def _lead_service(
    repository: FakeSignalRepository,
    pipeline_executor: SignalPipelineExecutor,
) -> LeadIntakeService:
    return LeadIntakeService(
        repository,
        agent_execution_service=AgentExecutionService(
            repository,
            pipeline_executor=pipeline_executor,
        ),
    )


@pytest.mark.asyncio
async def test_pipeline_scores_and_drafts_gate_passed_lead() -> None:
    public_data_client = FakePublicDataClient()
    repository = FakeSignalRepository()
    service = _lead_service(
        repository,
        SignalPipelineExecutor(
            settings=Settings(knowledge_graph_enabled=False),
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
    assert result.knowledge_graph.nodes
    assert result.knowledge_graph.edges
    assert result.knowledge_graph.warnings == [
        "knowledge graph storage disabled; returned current lead graph only"
    ]
    assert public_data_client.calls == 1


@pytest.mark.asyncio
async def test_pipeline_suppresses_draft_for_gate_failed_lead() -> None:
    repository = FakeSignalRepository()
    service = _lead_service(
        repository,
        SignalPipelineExecutor(
            settings=Settings(knowledge_graph_enabled=False),
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
    assert result.knowledge_graph.nodes
    assert "personal email domain" in result.flags


@pytest.mark.asyncio
async def test_pipeline_marks_model_failure_without_fallback_draft(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def failing_acompletion(**kwargs):
        raise RuntimeError("model unavailable")

    monkeypatch.setattr("litellm.acompletion", failing_acompletion)
    repository = FakeSignalRepository()
    service = _lead_service(
        repository,
        SignalPipelineExecutor(
            settings=Settings(knowledge_graph_enabled=False),
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
    runs = await AgentRunService(repository).list_agent_runs()

    assert result.gates.status == "passed"
    assert result.draft is None
    assert "model drafting failed" in result.flags
    assert runs[0].status == "failed"
    assert runs[0].current_stage == "model_drafting_failed"
    assert result.knowledge_graph.warnings == [
        "knowledge graph storage disabled; returned current lead graph only"
    ]


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
    repository = FakeSignalRepository()
    service = _lead_service(
        repository,
        SignalPipelineExecutor(
            settings=Settings(knowledge_graph_enabled=False),
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


@pytest.mark.asyncio
async def test_graph_failure_surfaces_warning_without_hiding_model_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def failing_acompletion(**kwargs):
        raise RuntimeError("model unavailable")

    monkeypatch.setattr("litellm.acompletion", failing_acompletion)
    repository = FakeSignalRepository()
    service = _lead_service(
        repository,
        SignalPipelineExecutor(
            settings=Settings(knowledge_graph_enabled=True),
            public_data_client=FakePublicDataClient(),
            knowledge_graph_service=KnowledgeGraphService(
                FailingKnowledgeGraphRepository(),
                storage_enabled=True,
            ),
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

    assert result.draft is None
    assert "model drafting failed" in result.flags
    assert result.knowledge_graph.warnings == [
        "knowledge graph storage unavailable; returned current lead graph only",
        "knowledge graph retrieval unavailable; returned current lead graph only",
    ]


class FailingKnowledgeGraphRepository:
    async def ingest_lead_graph(self, record, graph) -> None:
        raise RuntimeError("unavailable")

    async def find_related_leads(self, record):
        raise RuntimeError("unavailable")

    async def close(self) -> None:
        return None
