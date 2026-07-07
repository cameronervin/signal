import pytest

from app.workers import app as worker_app
from app.workers.tasks import _execute_signal_agent_run
from tests.fakes import FakePublicDataClient


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


@pytest.mark.asyncio
async def test_worker_execution_returns_json_safe_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.agents.executors.signal_pipeline.get_public_data_client",
        lambda settings: FakePublicDataClient(),
    )

    result = await _execute_signal_agent_run(
        {
            "lead_id": "lead_test",
            "run_id": "run_test",
            "lead": {
                "contact_name": "Sarah Chen",
                "email": "sarah@meridianresidential.example",
                "company": "Meridian Residential",
                "role": "VP Leasing",
                "property_address": "123 Market St",
                "city": "Austin",
                "state": "TX",
                "country": "US",
            },
            "activity_log": ["api_insert: lead received"],
        }
    )

    assert result["gates"]["status"] == "passed"
    assert result["score"]["tier"] == "A"
    assert result["draft"]["body"]


def test_worker_execution_reuses_initialized_resources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    worker_app.teardown_worker_resources()
    worker_app.init_worker_resources()
    graph_provider, public_data_client = worker_app.get_worker_resources()
    captured: dict[str, object] = {}

    class FakeExecutor:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)

        async def execute(self, initial_state: dict[str, object]) -> dict[str, object]:
            return initial_state

    monkeypatch.setattr(
        "app.workers.tasks.SignalPipelineExecutor",
        FakeExecutor,
    )

    result = worker_app.run_async(
        _execute_signal_agent_run(
            {
                "lead_id": "lead_test",
                "run_id": "run_test",
                "lead": {
                    "contact_name": "Sarah Chen",
                    "email": "sarah@meridianresidential.example",
                    "company": "Meridian Residential",
                    "role": "VP Leasing",
                    "property_address": "123 Market St",
                    "city": "Austin",
                    "state": "TX",
                    "country": "US",
                },
                "activity_log": ["api_insert: lead received"],
            }
        )
    )

    assert captured["graph_provider"] is graph_provider
    assert captured["public_data_client"] is public_data_client
    assert result["lead"]["email"] == "sarah@meridianresidential.example"
    worker_app.teardown_worker_resources()
