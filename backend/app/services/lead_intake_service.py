from typing import Protocol
from uuid import UUID, uuid4

from app.repositories.signal_snapshot import SignalRepository
from app.schemas.lead import (
    LeadCreate,
    LeadDeleteResponse,
    LeadQueueItemResponse,
    LeadResponse,
)
from app.schemas.run import AgentRunResponse
from app.services.agent_execution_service import AgentExecutionService


class AgentTaskDispatcher(Protocol):
    def enqueue_agent_run(self, run_id: UUID) -> None: ...


class CeleryAgentTaskDispatcher:
    def enqueue_agent_run(self, run_id: UUID) -> None:
        from app.workers.tasks import execute_signal_agent_run

        execute_signal_agent_run.apply_async(
            args=(str(run_id),),
            task_id=str(run_id),
        )


class QueueDispatchError(RuntimeError):
    """Raised when an agent run cannot be queued with the worker broker."""


class LeadDeleteNotFoundError(ValueError):
    """Raised when no lead intelligence records exist for deletion."""


class LeadDeleteConflictError(ValueError):
    """Raised when a lead cannot be deleted because worker state depends on it."""


class LeadIntakeService:
    """Use cases for inbound lead intake and lead retrieval."""

    def __init__(
        self,
        repository: SignalRepository,
        *,
        agent_execution_service: AgentExecutionService,
        task_dispatcher: AgentTaskDispatcher | None = None,
    ) -> None:
        self.repository = repository
        self.agent_execution_service = agent_execution_service
        self.task_dispatcher = task_dispatcher or CeleryAgentTaskDispatcher()

    async def create_and_enqueue(self, lead: LeadCreate) -> AgentRunResponse:
        return await self.create_and_enqueue_with_ids(
            lead=lead,
            lead_id=uuid4(),
            run_id=uuid4(),
            trigger="api_insert",
        )

    async def create_and_enqueue_with_ids(
        self,
        *,
        lead: LeadCreate,
        lead_id: UUID,
        run_id: UUID,
        trigger: str,
    ) -> AgentRunResponse:
        run = self.agent_execution_service.build_queued_run_response(
            lead_id=lead_id,
            run_id=run_id,
            trigger=trigger,
        )
        await self.repository.create_queued_agent_run(
            run=run,
            lead=lead,
            task_id=run_id,
        )
        await self.repository.commit()
        try:
            self.task_dispatcher.enqueue_agent_run(run_id)
        except Exception as exc:  # noqa: BLE001
            failed = self.agent_execution_service._build_failed_run_response(
                lead_id=lead_id,
                run_id=run_id,
                trigger=trigger,
                activity_log=[*run.activity_log, "agent_dispatch: failed"],
            )
            await self.repository.save_agent_run(failed)
            await self.repository.commit()
            raise QueueDispatchError("Agent run could not be queued") from exc
        return run

    async def create_and_enrich_with_ids(
        self,
        *,
        lead: LeadCreate,
        lead_id: UUID,
        run_id: UUID,
        trigger: str,
    ) -> LeadResponse:
        return await self.agent_execution_service.execute_for_inbound_lead(
            lead=lead,
            lead_id=lead_id,
            run_id=run_id,
            trigger=trigger,
        )

    async def create_and_enrich(self, lead: LeadCreate) -> LeadResponse:
        return await self.create_and_enrich_with_ids(
            lead=lead,
            lead_id=uuid4(),
            run_id=uuid4(),
            trigger="api_insert",
        )

    async def list_leads(self) -> list[LeadResponse]:
        return await self.repository.list_leads()

    async def list_lead_queue_items(self) -> list[LeadQueueItemResponse]:
        return await self.repository.list_lead_queue_items()

    async def get_lead(self, lead_id: UUID) -> LeadResponse | None:
        return await self.repository.get_lead(lead_id)

    async def delete_lead(
        self,
        lead_id: UUID,
        *,
        include_digital_worker: bool = False,
    ) -> LeadDeleteResponse:
        result = await self.repository.delete_lead_intelligence(
            lead_id,
            include_digital_worker=include_digital_worker,
        )
        if result.skipped_assigned_leads:
            raise LeadDeleteConflictError(
                "Lead has an active or paused Digital Workforce assignment"
            )
        if (
            result.deleted_leads == 0
            and result.deleted_agent_runs == 0
            and result.deleted_status_events == 0
        ):
            raise LeadDeleteNotFoundError("Lead not found")
        await self.repository.commit()
        return result

    async def delete_all_leads(self) -> LeadDeleteResponse:
        result = await self.repository.delete_all_lead_intelligence()
        await self.repository.commit()
        return result
