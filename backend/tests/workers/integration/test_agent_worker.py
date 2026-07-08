import pytest

from app.agents.utils.scoring import score_lead
from app.infrastructure.public_data.fixtures import demo_enrichment
from app.schemas.lead import GateResult, LeadCreate
from app.services.agent_execution_service import AgentExecutionService
from app.workers import app as worker_app
from app.workers.tasks import _execute_signal_agent_run
from tests.fakes import FakePublicDataClient, FakeSignalRepository


@pytest.fixture(autouse=True)
def disable_live_worker_tracing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(worker_app, "init_langfuse", lambda app_settings: False)
    monkeypatch.setattr(
        worker_app,
        "verify_tracing_configuration",
        lambda app_settings: {"enabled": False, "provider": "langfuse"},
    )
    monkeypatch.setattr(worker_app, "shutdown_langfuse", lambda: None)


def test_worker_resource_lifecycle_is_idempotent() -> None:
    worker_app.teardown_worker_resources()

    worker_app.init_worker_resources()
    first_loop = worker_app._worker_loop
    first_http_client = worker_app._worker_http_client
    first_resources = worker_app.get_worker_resources()
    worker_app.init_worker_resources()

    assert worker_app._worker_loop is first_loop
    assert worker_app._worker_http_client is first_http_client
    assert worker_app.get_worker_resources() == first_resources

    worker_app.teardown_worker_resources()

    assert first_http_client is not None
    assert first_http_client.is_closed is True
    assert worker_app.get_worker_resources() is None
    assert worker_app._worker_loop is None


def test_worker_lifecycle_initializes_and_shutdowns_langfuse(monkeypatch) -> None:
    calls: list[str] = []
    worker_app.teardown_worker_resources()

    def fake_init_langfuse(app_settings) -> bool:
        assert app_settings is worker_app.settings
        calls.append("init")
        return True

    def fake_verify(app_settings) -> dict[str, object]:
        assert app_settings is worker_app.settings
        calls.append("verify")
        return {"enabled": True, "provider": "langfuse", "ready": True}

    monkeypatch.setattr(worker_app, "init_langfuse", fake_init_langfuse)
    monkeypatch.setattr(worker_app, "verify_tracing_configuration", fake_verify)
    monkeypatch.setattr(
        worker_app,
        "shutdown_langfuse",
        lambda: calls.append("shutdown"),
    )

    worker_app.init_worker_resources()
    worker_app.init_worker_resources()
    worker_app.teardown_worker_resources()

    assert calls.count("init") == 1
    assert calls.count("verify") == 1
    assert calls[-1] == "shutdown"


def test_worker_shutdown_signal_tears_down_ready_resources() -> None:
    worker_app.teardown_worker_resources()
    worker_app.init_worker_resources()
    first_http_client = worker_app._worker_http_client

    worker_app.worker_shutdown.send(sender=None)

    assert first_http_client is not None
    assert first_http_client.is_closed is True
    assert worker_app.get_worker_resources() is None
    assert worker_app._worker_loop is None


@pytest.mark.asyncio
async def test_worker_execution_returns_json_safe_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = FakeSignalRepository()
    lead = _lead()
    run = AgentExecutionService(repository).build_queued_run_response(
        lead_id=_lead_id(),
        run_id=_run_id(),
        trigger="api_insert",
    )
    await repository.create_queued_agent_run(run=run, lead=lead, task_id=run.run_id)
    monkeypatch.setattr(
        "app.agents.executors.signal_pipeline.get_public_data_client",
        lambda settings: FakePublicDataClient(),
    )
    _patch_worker_repository(monkeypatch, repository)

    result = await _execute_signal_agent_run(str(run.run_id))
    leads = await repository.list_leads()

    assert result["status"] == "awaiting_review"
    assert result["current_stage"] == "human_review"
    assert leads[0].gates.status == "passed"
    assert leads[0].score.tier == "A"
    assert leads[0].draft is not None


def test_worker_execution_reuses_initialized_resources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    worker_app.teardown_worker_resources()
    worker_app.init_worker_resources()
    graph_provider, public_data_client, knowledge_graph_service = (
        worker_app.get_worker_resources()
    )
    captured: dict[str, object] = {}
    repository = FakeSignalRepository()
    lead = _lead()
    run = AgentExecutionService(repository).build_queued_run_response(
        lead_id=_lead_id(),
        run_id=_run_id(),
        trigger="api_insert",
    )
    worker_app.run_async(
        repository.create_queued_agent_run(run=run, lead=lead, task_id=run.run_id)
    )
    _patch_worker_repository(monkeypatch, repository)

    class FakeExecutor:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)

        async def execute(self, initial_state: dict[str, object]) -> dict[str, object]:
            gates = GateResult(status="failed", failures=["test gate"])
            enrichment = demo_enrichment(lead.company, lead.city, lead.state)
            return {
                **initial_state,
                "gates": gates,
                "enrichment": enrichment,
                "score": score_lead(lead, gates, enrichment),
                "draft": None,
            }

    monkeypatch.setattr(
        "app.workers.tasks.SignalPipelineExecutor",
        FakeExecutor,
    )

    result = worker_app.run_async(_execute_signal_agent_run(str(_run_id())))

    assert captured["graph_provider"] is graph_provider
    assert captured["public_data_client"] is public_data_client
    assert captured["knowledge_graph_service"] is knowledge_graph_service
    assert result["status"] == "completed"
    worker_app.teardown_worker_resources()


def _lead() -> LeadCreate:
    return LeadCreate(
        contact_name="Sarah Chen",
        email="sarah@meridianresidential.example",
        company="Meridian Residential",
        role="VP Leasing",
        property_address="123 Market St",
        city="Austin",
        state="TX",
        country="US",
    )


def _lead_id():
    from uuid import UUID

    return UUID("11111111-1111-4111-8111-111111111111")


def _run_id():
    from uuid import UUID

    return UUID("22222222-2222-4222-8222-222222222222")


class FakeSessionContext:
    def begin(self) -> "FakeSessionContext":
        return self

    async def __aenter__(self) -> object:
        return object()

    async def __aexit__(self, *args: object) -> None:
        return None


def _patch_worker_repository(
    monkeypatch: pytest.MonkeyPatch,
    repository: FakeSignalRepository,
) -> None:
    monkeypatch.setattr(
        "app.workers.tasks.get_sessionmaker",
        lambda: FakeSessionContext(),
    )
    monkeypatch.setattr(
        "app.workers.tasks.SignalSnapshotRepository",
        lambda session: repository,
    )
