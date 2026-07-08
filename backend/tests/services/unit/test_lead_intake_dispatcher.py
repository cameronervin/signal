from uuid import UUID

from app.services.lead_intake_service import CeleryAgentTaskDispatcher


def test_celery_dispatcher_enqueues_run_id_as_positional_argument(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_apply_async(**kwargs: object) -> None:
        captured.update(kwargs)

    monkeypatch.setattr(
        "app.workers.tasks.execute_signal_agent_run.apply_async",
        fake_apply_async,
    )

    run_id = UUID("64132fbc-eba5-4988-9f12-0e31b98a87f2")
    CeleryAgentTaskDispatcher().enqueue_agent_run(run_id)

    assert captured == {
        "args": (str(run_id),),
        "task_id": str(run_id),
    }
