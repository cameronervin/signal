from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from app.agents.context.digital_worker_lifecycle import (
    DigitalWorkerLifecycleSpec,
    load_default_lifecycle_spec,
)
from app.agents.executors.digital_worker import DigitalWorkerExecutor
from app.agents.tools.digital_worker import DigitalWorkerTools
from app.repositories.digital_worker import DigitalWorkerRepository
from app.repositories.signal_snapshot import SignalRepository
from app.schemas.digital_worker import (
    DigitalWorkerAssignmentCreate,
    DigitalWorkerAssignmentResponse,
    DigitalWorkerInboundEmailCreate,
    DigitalWorkerRunResponse,
)


class DigitalWorkerTaskDispatcher(Protocol):
    def enqueue_digital_worker_run(self, run_id: UUID) -> None: ...


class CeleryDigitalWorkerTaskDispatcher:
    def enqueue_digital_worker_run(self, run_id: UUID) -> None:
        from app.workers.tasks import execute_digital_worker_run

        execute_digital_worker_run.apply_async(
            args=(str(run_id),),
            task_id=str(run_id),
        )


class DigitalWorkerServiceError(ValueError):
    """Base service error for worker transition failures."""


class DigitalWorkerNotFoundError(DigitalWorkerServiceError):
    """Raised when a worker assignment or run is missing."""


class DigitalWorkerEligibilityError(DigitalWorkerServiceError):
    """Raised when a lead cannot be assigned to the worker."""


class DigitalWorkerTransitionError(DigitalWorkerServiceError):
    """Raised when a worker transition is invalid."""


class DigitalWorkerDispatchError(RuntimeError):
    """Raised when a worker run cannot be queued."""


class DigitalWorkerService:
    def __init__(
        self,
        *,
        signal_repository: SignalRepository,
        worker_repository: DigitalWorkerRepository,
        lifecycle: DigitalWorkerLifecycleSpec | None = None,
        task_dispatcher: DigitalWorkerTaskDispatcher | None = None,
    ) -> None:
        self.signal_repository = signal_repository
        self.worker_repository = worker_repository
        self.lifecycle = lifecycle or load_default_lifecycle_spec()
        self.task_dispatcher = task_dispatcher or CeleryDigitalWorkerTaskDispatcher()
        self.tools = DigitalWorkerTools(worker_repository)

    async def assign_lead(
        self,
        payload: DigitalWorkerAssignmentCreate,
    ) -> DigitalWorkerAssignmentResponse:
        lead = await self.signal_repository.get_lead(payload.lead_id)
        if lead is None:
            raise DigitalWorkerNotFoundError("Lead not found")
        if lead.gates.status != "passed" or lead.draft is None:
            raise DigitalWorkerEligibilityError(
                "Only gate-passed leads with drafts can be assigned"
            )
        existing = await self.worker_repository.get_active_assignment_for_lead(
            payload.lead_id
        )
        if existing is not None:
            raise DigitalWorkerTransitionError(
                "Lead already has an active digital worker assignment"
            )

        assignment = await self.worker_repository.create_assignment(
            lead_id=payload.lead_id,
            lifecycle=self.lifecycle,
        )
        run = await self.worker_repository.create_run(
            assignment_id=assignment.assignment_id,
            trigger="assignment_created",
        )
        await self.worker_repository.commit()
        try:
            self.task_dispatcher.enqueue_digital_worker_run(run.run_id)
        except Exception as exc:  # noqa: BLE001
            await self.worker_repository.update_run_status(
                run_id=run.run_id,
                status="failed",
                message="digital worker dispatch failed",
            )
            assignment = await self.worker_repository.update_assignment_state(
                assignment_id=assignment.assignment_id,
                status="failed",
                activity="dispatch: failed",
            )
            await self.worker_repository.commit()
            raise DigitalWorkerDispatchError(
                "Digital worker run could not be queued"
            ) from exc
        return await self.get_assignment(assignment.assignment_id)

    async def list_assignments(self) -> list[DigitalWorkerAssignmentResponse]:
        return await self.worker_repository.list_assignments()

    async def get_assignment(
        self,
        assignment_id: UUID,
    ) -> DigitalWorkerAssignmentResponse:
        assignment = await self.worker_repository.get_assignment(assignment_id)
        if assignment is None:
            raise DigitalWorkerNotFoundError("Assignment not found")
        return assignment

    async def record_inbound_email(
        self,
        *,
        assignment_id: UUID,
        payload: DigitalWorkerInboundEmailCreate,
    ) -> DigitalWorkerAssignmentResponse:
        assignment = await self.get_assignment(assignment_id)
        if assignment.status != "active":
            raise DigitalWorkerTransitionError(
                f"Cannot trigger worker for {assignment.status!r} assignment"
            )
        await self.tools.record_inbound_email(
            assignment_id=assignment_id,
            subject=payload.subject,
            body=payload.body,
            external_message_id=payload.external_message_id,
        )
        run = await self.worker_repository.create_run(
            assignment_id=assignment_id,
            trigger="inbound_email",
        )
        await self.worker_repository.commit()
        try:
            self.task_dispatcher.enqueue_digital_worker_run(run.run_id)
        except Exception as exc:  # noqa: BLE001
            await self.worker_repository.update_run_status(
                run_id=run.run_id,
                status="failed",
                message="digital worker dispatch failed",
            )
            await self.worker_repository.commit()
            raise DigitalWorkerDispatchError(
                "Digital worker run could not be queued"
            ) from exc
        return await self.get_assignment(assignment_id)

    async def pause_assignment(
        self,
        assignment_id: UUID,
    ) -> DigitalWorkerAssignmentResponse:
        assignment = await self.get_assignment(assignment_id)
        if assignment.status != "active":
            raise DigitalWorkerTransitionError(
                f"Cannot pause {assignment.status!r} assignment"
            )
        updated = await self.worker_repository.update_assignment_state(
            assignment_id=assignment_id,
            status="paused",
            activity="assignment: paused",
        )
        await self.worker_repository.commit()
        if updated is None:
            raise DigitalWorkerNotFoundError("Assignment not found")
        return updated

    async def resume_assignment(
        self,
        assignment_id: UUID,
    ) -> DigitalWorkerAssignmentResponse:
        assignment = await self.get_assignment(assignment_id)
        if assignment.status != "paused":
            raise DigitalWorkerTransitionError(
                f"Cannot resume {assignment.status!r} assignment"
            )
        updated = await self.worker_repository.update_assignment_state(
            assignment_id=assignment_id,
            status="active",
            activity="assignment: resumed",
        )
        run = await self.worker_repository.create_run(
            assignment_id=assignment_id,
            trigger="manual_resume",
        )
        await self.worker_repository.commit()
        try:
            self.task_dispatcher.enqueue_digital_worker_run(run.run_id)
        except Exception as exc:  # noqa: BLE001
            await self.worker_repository.update_run_status(
                run_id=run.run_id,
                status="failed",
                message="digital worker dispatch failed",
            )
            await self.worker_repository.commit()
            raise DigitalWorkerDispatchError(
                "Digital worker run could not be queued"
            ) from exc
        if updated is None:
            raise DigitalWorkerNotFoundError("Assignment not found")
        return await self.get_assignment(assignment_id)

    async def execute_run(self, run_id: UUID) -> DigitalWorkerRunResponse:
        run = await self.worker_repository.get_run(run_id)
        if run is None:
            raise DigitalWorkerNotFoundError("Run not found")
        assignment = await self.get_assignment(run.assignment_id)
        if assignment.status != "active":
            skipped = await self.worker_repository.update_run_status(
                run_id=run_id,
                status="skipped",
                message=f"assignment is {assignment.status}",
            )
            await self.worker_repository.commit()
            if skipped is None:
                raise DigitalWorkerNotFoundError("Run not found")
            return skipped

        running = await self.worker_repository.update_run_status(
            run_id=run_id,
            status="running",
            message="digital worker running",
        )
        if running is None:
            raise DigitalWorkerNotFoundError("Run not found")

        try:
            await DigitalWorkerExecutor(
                signal_repository=self.signal_repository,
                worker_repository=self.worker_repository,
                lifecycle=self.lifecycle,
            ).execute(run_id)
            await self.worker_repository.complete_claimed_follow_ups(run_id=run_id)
            completed = await self.worker_repository.update_run_status(
                run_id=run_id,
                status="completed",
                message="digital worker completed one wake-up",
            )
            await self.worker_repository.commit()
        except Exception:
            failed = await self.worker_repository.update_run_status(
                run_id=run_id,
                status="failed",
                message="digital worker execution failed",
            )
            await self.worker_repository.commit()
            if failed is None:
                raise
            raise
        if completed is None:
            raise DigitalWorkerNotFoundError("Run not found")
        return completed

    async def claim_due_follow_ups(
        self,
        *,
        now: datetime | None = None,
        limit: int = 25,
    ) -> list[DigitalWorkerRunResponse]:
        runs = await self.worker_repository.claim_due_follow_ups(
            now=now or datetime.now(UTC),
            limit=limit,
        )
        await self.worker_repository.commit()
        return runs
