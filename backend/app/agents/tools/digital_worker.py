from datetime import datetime
from uuid import UUID

from app.repositories.digital_worker import DigitalWorkerRepository
from app.schemas.digital_worker import (
    DigitalWorkerFollowUpResponse,
    DigitalWorkerMessageResponse,
)

DIGITAL_WORKER_SEND_SANDBOX_EMAIL_TOOL = "send_sandbox_email"
DIGITAL_WORKER_RECORD_INBOUND_EMAIL_TOOL = "record_inbound_email"
DIGITAL_WORKER_SCHEDULE_FOLLOW_UP_TOOL = "schedule_follow_up"
DIGITAL_WORKER_MARK_GOAL_COMPLETE_TOOL = "mark_goal_complete"
DIGITAL_WORKER_MARK_PHASE_OUTCOME_TOOL = "mark_phase_outcome"

DIGITAL_WORKER_TOOL_DESCRIPTIONS: dict[str, str] = {
    DIGITAL_WORKER_SEND_SANDBOX_EMAIL_TOOL: (
        "Persist an outbound sandbox email for the assigned lead. This tool "
        "never calls a live email provider."
    ),
    DIGITAL_WORKER_RECORD_INBOUND_EMAIL_TOOL: (
        "Persist an inbound sandbox email body for worker context. Do not log "
        "the body or full email address."
    ),
    DIGITAL_WORKER_SCHEDULE_FOLLOW_UP_TOOL: (
        "Create a due follow-up row for the heartbeat scanner to claim later."
    ),
    DIGITAL_WORKER_MARK_GOAL_COMPLETE_TOOL: (
        "Mark one lifecycle goal complete for the current worker assignment."
    ),
    DIGITAL_WORKER_MARK_PHASE_OUTCOME_TOOL: (
        "Update the assignment phase or terminal status after a bounded "
        "worker wake-up."
    ),
}


class DigitalWorkerTools:
    """Explicit tool boundary for the SDR digital worker.

    These methods only write sandbox communication and worker state. They do not
    call live email, SMS, CRM, scoring, or enrichment providers.
    """

    def __init__(self, repository: DigitalWorkerRepository) -> None:
        self.repository = repository

    async def send_sandbox_email(
        self,
        *,
        assignment_id: UUID,
        subject: str,
        body: str,
    ) -> DigitalWorkerMessageResponse:
        return await self.repository.add_message(
            assignment_id=assignment_id,
            direction="outbound",
            subject=subject,
            body=body,
        )

    async def record_inbound_email(
        self,
        *,
        assignment_id: UUID,
        subject: str,
        body: str,
        external_message_id: str | None,
    ) -> DigitalWorkerMessageResponse:
        return await self.repository.add_message(
            assignment_id=assignment_id,
            direction="inbound",
            subject=subject,
            body=body,
            external_message_id=external_message_id,
        )

    async def schedule_follow_up(
        self,
        *,
        assignment_id: UUID,
        due_at: datetime,
        reason: str,
    ) -> DigitalWorkerFollowUpResponse:
        return await self.repository.schedule_follow_up(
            assignment_id=assignment_id,
            due_at=due_at,
            reason=reason,
        )

    async def mark_goal_complete(
        self,
        *,
        assignment_id: UUID,
        phase_key: str,
        goal_key: str,
        notes: str | None = None,
    ) -> None:
        await self.repository.complete_goal(
            assignment_id=assignment_id,
            phase_key=phase_key,
            goal_key=goal_key,
            notes=notes,
        )

    async def mark_phase_outcome(
        self,
        *,
        assignment_id: UUID,
        status: str | None = None,
        current_phase: str | None = None,
        activity: str | None = None,
    ) -> None:
        await self.repository.update_assignment_state(
            assignment_id=assignment_id,
            status=status,
            current_phase=current_phase,
            activity=activity,
        )
