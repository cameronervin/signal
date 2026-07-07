import asyncio
from typing import Any

from pydantic import BaseModel

from app.agents.executors.signal_pipeline import SignalPipelineExecutor
from app.agents.states.signal_state import SignalState
from app.schemas.lead import LeadCreate
from app.workers.app import celery_app


@celery_app.task(name="signal.agent_runs.execute")
def execute_signal_agent_run(initial_state: dict[str, Any]) -> dict[str, Any]:
    """Run the Signal agent graph in a Celery worker.

    This task is intentionally payload-only for now. The current HTTP endpoint
    still runs inline so it can return the existing LeadResponse contract.
    """
    return asyncio.run(_execute_signal_agent_run(initial_state))


async def _execute_signal_agent_run(initial_state: dict[str, Any]) -> dict[str, Any]:
    state: SignalState = {
        **initial_state,
        "lead": LeadCreate.model_validate(initial_state["lead"]),
    }
    result = await SignalPipelineExecutor().execute(state)
    return _json_safe(result)


def _json_safe(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value
