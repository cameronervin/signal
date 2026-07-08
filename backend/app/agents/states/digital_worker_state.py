from typing import NotRequired, TypedDict
from uuid import UUID

from app.schemas.digital_worker import (
    DigitalWorkerAssignmentResponse,
    DigitalWorkerRunResponse,
    DigitalWorkerTrigger,
)
from app.schemas.lead import LeadResponse


class DigitalWorkerState(TypedDict):
    run_id: UUID
    assignment_id: NotRequired[UUID]
    trigger: NotRequired[DigitalWorkerTrigger]
    run: NotRequired[DigitalWorkerRunResponse]
    assignment: NotRequired[DigitalWorkerAssignmentResponse]
    lead: NotRequired[LeadResponse]
    activity_log: NotRequired[list[str]]
