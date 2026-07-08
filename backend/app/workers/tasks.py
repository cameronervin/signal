from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.agents.executors.signal_pipeline import SignalPipelineExecutor
from app.infrastructure.db.session import get_sessionmaker
from app.repositories.signal_snapshot import SignalSnapshotRepository
from app.services.agent_execution_service import AgentExecutionService
from app.workers.app import celery_app, get_worker_resources, run_async

TERMINAL_OR_HELD_STATUSES = {"awaiting_review", "completed", "failed", "paused"}


@celery_app.task(name="signal.agent_runs.execute")
def execute_signal_agent_run(run_id: str) -> dict[str, Any]:
    """Run the Signal agent graph in a Celery worker.

    Postgres is the source of truth for run status and completed lead snapshots.
    Celery's result backend is only operational metadata.
    """
    return run_async(_execute_signal_agent_run(run_id))


async def _execute_signal_agent_run(run_id: str) -> dict[str, Any]:
    parsed_run_id = UUID(run_id)
    session_factory = get_sessionmaker()

    async with session_factory.begin() as session:
        repository = SignalSnapshotRepository(session)
        run = await repository.get_agent_run(parsed_run_id)
        lead = await repository.get_agent_run_input(parsed_run_id)
        if run is None or lead is None:
            return {"run_id": run_id, "status": "missing"}
        if run.status in TERMINAL_OR_HELD_STATUSES or run.status == "running":
            return run.model_dump(mode="json")
        running = AgentExecutionService(repository).build_running_run_response(run)
        await repository.save_agent_run(running)

    worker_resources = get_worker_resources()
    if worker_resources is None:
        executor = SignalPipelineExecutor()
    else:
        graph_provider, public_data_client, knowledge_graph_service = worker_resources
        executor = SignalPipelineExecutor(
            graph_provider=graph_provider,
            public_data_client=public_data_client,
            knowledge_graph_service=knowledge_graph_service,
        )
    execution_service = AgentExecutionService(
        SignalSnapshotRepositoryPlaceholder(),
        pipeline_executor=executor,
    )
    try:
        lead_response, final_run = await execution_service.execute_pipeline(
            lead=lead,
            lead_id=run.lead_id,
            run_id=run.run_id,
            trigger=run.trigger,
        )
    except Exception:
        async with session_factory.begin() as session:
            repository = SignalSnapshotRepository(session)
            failed = AgentExecutionService(repository)._build_failed_run_response(
                lead_id=run.lead_id,
                run_id=run.run_id,
                trigger=run.trigger,
                activity_log=[*run.activity_log, "agent_execution: failed"],
            )
            await repository.save_agent_run(failed)
        raise

    async with session_factory.begin() as session:
        repository = SignalSnapshotRepository(session)
        current_run = await repository.get_agent_run(parsed_run_id)
        if current_run is None:
            return {"run_id": run_id, "status": "missing"}
        if current_run.status == "paused":
            await repository.append_status_event(
                run_id=parsed_run_id,
                status="paused",
                current_stage=current_run.current_stage,
                message="worker completed after pause; result not published",
            )
            return current_run.model_dump(mode="json")
        if final_run.status in {"awaiting_review", "completed"}:
            await repository.save_lead(lead_response)
        await repository.save_agent_run(final_run)
    return final_run.model_dump(mode="json")


def _json_safe(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


class SignalSnapshotRepositoryPlaceholder:
    """Placeholder for response-builder methods that do not use persistence."""
