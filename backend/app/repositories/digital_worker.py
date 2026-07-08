from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.context.digital_worker_lifecycle import DigitalWorkerLifecycleSpec
from app.models.signal import (
    DigitalWorkerAssignmentRecord,
    DigitalWorkerFollowUpRecord,
    DigitalWorkerGoalStateRecord,
    DigitalWorkerMessageRecord,
    DigitalWorkerRunRecord,
)
from app.schemas.digital_worker import (
    DigitalWorkerAssignmentResponse,
    DigitalWorkerFollowUpResponse,
    DigitalWorkerGoalStateResponse,
    DigitalWorkerMessageResponse,
    DigitalWorkerRunResponse,
    DigitalWorkerTrigger,
)


class DigitalWorkerRepository(Protocol):
    async def commit(self) -> None: ...

    async def create_assignment(
        self,
        *,
        lead_id: UUID,
        lifecycle: DigitalWorkerLifecycleSpec,
    ) -> DigitalWorkerAssignmentResponse: ...

    async def list_assignments(self) -> list[DigitalWorkerAssignmentResponse]: ...

    async def get_assignment(
        self,
        assignment_id: UUID,
    ) -> DigitalWorkerAssignmentResponse | None: ...

    async def get_active_assignment_for_lead(
        self,
        lead_id: UUID,
    ) -> DigitalWorkerAssignmentResponse | None: ...

    async def create_run(
        self,
        *,
        assignment_id: UUID,
        trigger: DigitalWorkerTrigger,
    ) -> DigitalWorkerRunResponse: ...

    async def get_run(self, run_id: UUID) -> DigitalWorkerRunResponse | None: ...

    async def update_run_status(
        self,
        *,
        run_id: UUID,
        status: str,
        message: str | None = None,
    ) -> DigitalWorkerRunResponse | None: ...

    async def add_message(
        self,
        *,
        assignment_id: UUID,
        direction: str,
        subject: str,
        body: str,
        external_message_id: str | None = None,
    ) -> DigitalWorkerMessageResponse: ...

    async def complete_goal(
        self,
        *,
        assignment_id: UUID,
        phase_key: str,
        goal_key: str,
        notes: str | None = None,
    ) -> None: ...

    async def update_assignment_state(
        self,
        *,
        assignment_id: UUID,
        status: str | None = None,
        current_phase: str | None = None,
        activity: str | None = None,
    ) -> DigitalWorkerAssignmentResponse | None: ...

    async def schedule_follow_up(
        self,
        *,
        assignment_id: UUID,
        due_at: datetime,
        reason: str,
    ) -> DigitalWorkerFollowUpResponse: ...

    async def complete_claimed_follow_ups(self, *, run_id: UUID) -> None: ...

    async def claim_due_follow_ups(
        self,
        *,
        now: datetime,
        limit: int,
    ) -> list[DigitalWorkerRunResponse]: ...


class DigitalWorkerPostgresRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def create_assignment(
        self,
        *,
        lead_id: UUID,
        lifecycle: DigitalWorkerLifecycleSpec,
    ) -> DigitalWorkerAssignmentResponse:
        assignment_id = uuid4()
        activity_log = [
            "assignment: SDR assigned digital worker",
            "worker: lifecycle goals initialized",
        ]
        self.session.add(
            DigitalWorkerAssignmentRecord(
                assignment_id=assignment_id,
                lead_id=lead_id,
                status="active",
                current_phase=lifecycle.initial_phase,
                lifecycle_version=lifecycle.version,
                latest_run_id=None,
                payload={"activity_log": activity_log},
            )
        )
        for phase in lifecycle.phases:
            for goal in phase.goals:
                self.session.add(
                    DigitalWorkerGoalStateRecord(
                        id=uuid4(),
                        assignment_id=assignment_id,
                        phase_key=phase.key,
                        goal_key=goal.key,
                        status="pending",
                        notes=None,
                        payload={"description": goal.description},
                    )
                )
        await self.session.flush()
        assignment = await self.get_assignment(assignment_id)
        if assignment is None:
            raise RuntimeError("Digital worker assignment was not persisted")
        return assignment

    async def list_assignments(self) -> list[DigitalWorkerAssignmentResponse]:
        result = await self.session.scalars(
            select(DigitalWorkerAssignmentRecord).order_by(
                DigitalWorkerAssignmentRecord.created_at.desc()
            )
        )
        assignments: list[DigitalWorkerAssignmentResponse] = []
        for record in result:
            assignment = await self.get_assignment(record.assignment_id)
            if assignment is not None:
                assignments.append(assignment)
        return assignments

    async def get_assignment(
        self,
        assignment_id: UUID,
    ) -> DigitalWorkerAssignmentResponse | None:
        record = await self.session.get(DigitalWorkerAssignmentRecord, assignment_id)
        if record is None:
            return None
        return await self._assignment_response(record)

    async def get_active_assignment_for_lead(
        self,
        lead_id: UUID,
    ) -> DigitalWorkerAssignmentResponse | None:
        record = await self.session.scalar(
            select(DigitalWorkerAssignmentRecord)
            .where(DigitalWorkerAssignmentRecord.lead_id == lead_id)
            .where(DigitalWorkerAssignmentRecord.status.in_(("active", "paused")))
            .order_by(DigitalWorkerAssignmentRecord.created_at.desc())
            .limit(1)
        )
        if record is None:
            return None
        return await self._assignment_response(record)

    async def create_run(
        self,
        *,
        assignment_id: UUID,
        trigger: DigitalWorkerTrigger,
    ) -> DigitalWorkerRunResponse:
        assignment_record = await self.session.get(
            DigitalWorkerAssignmentRecord,
            assignment_id,
        )
        if assignment_record is None:
            raise ValueError("Assignment not found")
        run_id = uuid4()
        run = DigitalWorkerRunRecord(
            run_id=run_id,
            assignment_id=assignment_id,
            trigger=trigger,
            status="queued",
            current_phase=assignment_record.current_phase,
            message="digital worker queued",
            payload=None,
        )
        self.session.add(run)
        assignment_record.latest_run_id = run_id
        self._append_activity(assignment_record, f"{trigger}: worker queued")
        await self.session.flush()
        return _run_response(run)

    async def get_run(self, run_id: UUID) -> DigitalWorkerRunResponse | None:
        record = await self.session.get(DigitalWorkerRunRecord, run_id)
        if record is None:
            return None
        return _run_response(record)

    async def update_run_status(
        self,
        *,
        run_id: UUID,
        status: str,
        message: str | None = None,
    ) -> DigitalWorkerRunResponse | None:
        record = await self.session.get(DigitalWorkerRunRecord, run_id)
        if record is None:
            return None
        now = datetime.now(UTC)
        record.status = status
        if message is not None:
            record.message = message
        if status == "running" and record.started_at is None:
            record.started_at = now
        if status in {"completed", "skipped"}:
            record.completed_at = now
        if status == "failed":
            record.failed_at = now
        assignment = await self.session.get(
            DigitalWorkerAssignmentRecord,
            record.assignment_id,
        )
        if assignment is not None:
            record.current_phase = assignment.current_phase
            self._append_activity(assignment, f"worker_run: {status}")
        await self.session.flush()
        return _run_response(record)

    async def add_message(
        self,
        *,
        assignment_id: UUID,
        direction: str,
        subject: str,
        body: str,
        external_message_id: str | None = None,
    ) -> DigitalWorkerMessageResponse:
        record = DigitalWorkerMessageRecord(
            message_id=uuid4(),
            assignment_id=assignment_id,
            direction=direction,
            channel="email",
            subject=subject,
            body=body,
            external_message_id=external_message_id,
            payload=None,
        )
        self.session.add(record)
        assignment = await self.session.get(
            DigitalWorkerAssignmentRecord,
            assignment_id,
        )
        if assignment is not None:
            self._append_activity(assignment, f"email: {direction} sandbox message")
        await self.session.flush()
        return _message_response(record)

    async def complete_goal(
        self,
        *,
        assignment_id: UUID,
        phase_key: str,
        goal_key: str,
        notes: str | None = None,
    ) -> None:
        record = await self.session.scalar(
            select(DigitalWorkerGoalStateRecord)
            .where(DigitalWorkerGoalStateRecord.assignment_id == assignment_id)
            .where(DigitalWorkerGoalStateRecord.phase_key == phase_key)
            .where(DigitalWorkerGoalStateRecord.goal_key == goal_key)
        )
        if record is None or record.status == "completed":
            return
        record.status = "completed"
        record.completed_at = datetime.now(UTC)
        record.notes = notes
        assignment = await self.session.get(
            DigitalWorkerAssignmentRecord,
            assignment_id,
        )
        if assignment is not None:
            self._append_activity(assignment, f"goal: {goal_key} completed")

    async def update_assignment_state(
        self,
        *,
        assignment_id: UUID,
        status: str | None = None,
        current_phase: str | None = None,
        activity: str | None = None,
    ) -> DigitalWorkerAssignmentResponse | None:
        record = await self.session.get(DigitalWorkerAssignmentRecord, assignment_id)
        if record is None:
            return None
        now = datetime.now(UTC)
        if status is not None:
            record.status = status
            if status == "completed":
                record.completed_at = now
            if status == "failed":
                record.failed_at = now
        if current_phase is not None:
            record.current_phase = current_phase
        if activity is not None:
            self._append_activity(record, activity)
        await self.session.flush()
        return await self._assignment_response(record)

    async def schedule_follow_up(
        self,
        *,
        assignment_id: UUID,
        due_at: datetime,
        reason: str,
    ) -> DigitalWorkerFollowUpResponse:
        record = DigitalWorkerFollowUpRecord(
            follow_up_id=uuid4(),
            assignment_id=assignment_id,
            status="pending",
            due_at=due_at,
            reason=reason,
            claimed_run_id=None,
            payload=None,
        )
        self.session.add(record)
        assignment = await self.session.get(
            DigitalWorkerAssignmentRecord,
            assignment_id,
        )
        if assignment is not None:
            self._append_activity(assignment, "follow_up: scheduled")
        await self.session.flush()
        return _follow_up_response(record)

    async def complete_claimed_follow_ups(self, *, run_id: UUID) -> None:
        result = await self.session.scalars(
            select(DigitalWorkerFollowUpRecord)
            .where(DigitalWorkerFollowUpRecord.claimed_run_id == run_id)
            .where(DigitalWorkerFollowUpRecord.status == "claimed")
        )
        now = datetime.now(UTC)
        for record in result:
            record.status = "completed"
            record.completed_at = now

    async def claim_due_follow_ups(
        self,
        *,
        now: datetime,
        limit: int,
    ) -> list[DigitalWorkerRunResponse]:
        result = await self.session.scalars(
            select(DigitalWorkerFollowUpRecord)
            .where(DigitalWorkerFollowUpRecord.status == "pending")
            .where(DigitalWorkerFollowUpRecord.due_at <= now)
            .order_by(DigitalWorkerFollowUpRecord.due_at.asc())
            .limit(limit)
        )
        runs: list[DigitalWorkerRunResponse] = []
        for follow_up in result:
            assignment = await self.session.get(
                DigitalWorkerAssignmentRecord,
                follow_up.assignment_id,
            )
            if assignment is None or assignment.status != "active":
                follow_up.status = "cancelled"
                continue
            run_id = uuid4()
            run = DigitalWorkerRunRecord(
                run_id=run_id,
                assignment_id=assignment.assignment_id,
                trigger="follow_up_due",
                status="queued",
                current_phase=assignment.current_phase,
                message="follow-up due",
                payload={"follow_up_id": str(follow_up.follow_up_id)},
            )
            self.session.add(run)
            follow_up.status = "claimed"
            follow_up.claimed_run_id = run_id
            assignment.latest_run_id = run_id
            self._append_activity(assignment, "follow_up_due: worker queued")
            runs.append(_run_response(run))
        await self.session.flush()
        return runs

    async def _assignment_response(
        self,
        record: DigitalWorkerAssignmentRecord,
    ) -> DigitalWorkerAssignmentResponse:
        goals_result = await self.session.scalars(
            select(DigitalWorkerGoalStateRecord)
            .where(DigitalWorkerGoalStateRecord.assignment_id == record.assignment_id)
            .order_by(
                DigitalWorkerGoalStateRecord.phase_key.asc(),
                DigitalWorkerGoalStateRecord.created_at.asc(),
            )
        )
        messages_result = await self.session.scalars(
            select(DigitalWorkerMessageRecord)
            .where(DigitalWorkerMessageRecord.assignment_id == record.assignment_id)
            .order_by(DigitalWorkerMessageRecord.created_at.asc())
        )
        follow_ups_result = await self.session.scalars(
            select(DigitalWorkerFollowUpRecord)
            .where(DigitalWorkerFollowUpRecord.assignment_id == record.assignment_id)
            .order_by(DigitalWorkerFollowUpRecord.due_at.asc())
        )
        runs_result = await self.session.scalars(
            select(DigitalWorkerRunRecord)
            .where(DigitalWorkerRunRecord.assignment_id == record.assignment_id)
            .order_by(DigitalWorkerRunRecord.created_at.asc())
        )
        return DigitalWorkerAssignmentResponse(
            assignment_id=record.assignment_id,
            lead_id=record.lead_id,
            status=record.status,
            current_phase=record.current_phase,
            lifecycle_version=record.lifecycle_version,
            latest_run_id=record.latest_run_id,
            activity_log=list((record.payload or {}).get("activity_log", [])),
            created_at=record.created_at,
            updated_at=record.updated_at,
            goals=[_goal_response(goal) for goal in goals_result],
            messages=[_message_response(message) for message in messages_result],
            follow_ups=[
                _follow_up_response(follow_up) for follow_up in follow_ups_result
            ],
            runs=[_run_response(run) for run in runs_result],
        )

    def _append_activity(
        self,
        record: DigitalWorkerAssignmentRecord,
        activity: str,
    ) -> None:
        payload = dict(record.payload or {})
        activity_log = list(payload.get("activity_log", []))
        activity_log.append(activity)
        payload["activity_log"] = activity_log[-100:]
        record.payload = payload


def _goal_response(
    record: DigitalWorkerGoalStateRecord,
) -> DigitalWorkerGoalStateResponse:
    return DigitalWorkerGoalStateResponse(
        phase_key=record.phase_key,
        goal_key=record.goal_key,
        status=record.status,
        completed_at=record.completed_at,
        notes=record.notes,
    )


def _message_response(
    record: DigitalWorkerMessageRecord,
) -> DigitalWorkerMessageResponse:
    return DigitalWorkerMessageResponse(
        message_id=record.message_id,
        assignment_id=record.assignment_id,
        direction=record.direction,
        channel="email",
        subject=record.subject,
        body=record.body,
        external_message_id=record.external_message_id,
        created_at=record.created_at,
    )


def _follow_up_response(
    record: DigitalWorkerFollowUpRecord,
) -> DigitalWorkerFollowUpResponse:
    return DigitalWorkerFollowUpResponse(
        follow_up_id=record.follow_up_id,
        assignment_id=record.assignment_id,
        status=record.status,
        due_at=record.due_at,
        reason=record.reason,
        claimed_run_id=record.claimed_run_id,
        created_at=record.created_at,
    )


def _run_response(record: DigitalWorkerRunRecord) -> DigitalWorkerRunResponse:
    return DigitalWorkerRunResponse(
        run_id=record.run_id,
        assignment_id=record.assignment_id,
        trigger=record.trigger,
        status=record.status,
        current_phase=record.current_phase,
        message=record.message,
        created_at=record.created_at,
        started_at=record.started_at,
        completed_at=record.completed_at,
        failed_at=record.failed_at,
    )
