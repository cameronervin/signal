from uuid import UUID

from app.repositories.signal_snapshot import SignalRepository
from app.schemas.run import AgentRunResponse, AgentStep


class RunTransitionError(ValueError):
    """Raised when an agent run transition is not allowed."""


class AgentRunService:
    """Use cases for polling and controlling agent runs."""

    def __init__(self, repository: SignalRepository) -> None:
        self.repository = repository

    async def list_agent_runs(self) -> list[AgentRunResponse]:
        return await self.repository.list_agent_runs()

    async def get_agent_run(self, run_id: UUID) -> AgentRunResponse | None:
        return await self.repository.get_agent_run(run_id)

    async def approve_agent_run(self, run_id: UUID) -> AgentRunResponse | None:
        run = await self.repository.get_agent_run(run_id)
        if run is None:
            return None
        if run.status != "awaiting_review":
            raise RunTransitionError(
                f"Cannot approve run in {run.status!r} status"
            )
        updated = run.model_copy(
            update={
                "status": "completed",
                "current_stage": "review_approved",
                "steps": _update_human_review_step(run.steps, "done"),
                "activity_log": [
                    *run.activity_log,
                    "human_review: approved without send",
                ],
            },
            deep=True,
        )
        await self.repository.save_agent_run(updated)
        return updated

    async def pause_agent_run(self, run_id: UUID) -> AgentRunResponse | None:
        run = await self.repository.get_agent_run(run_id)
        if run is None:
            return None
        if run.status not in {"queued", "running", "awaiting_review"}:
            raise RunTransitionError(f"Cannot pause run in {run.status!r} status")
        updated = run.model_copy(
            update={
                "status": "paused",
                "current_stage": f"{run.current_stage}_paused",
                "activity_log": [*run.activity_log, "agent_run: paused"],
            },
            deep=True,
        )
        await self.repository.save_agent_run(updated)
        return updated


def _update_human_review_step(
    steps: list[AgentStep],
    status: str,
) -> list[AgentStep]:
    return [
        step.model_copy(update={"status": status})
        if step.name == "Human review"
        else step
        for step in steps
    ]
