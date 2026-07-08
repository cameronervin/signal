from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

DigitalWorkerAssignmentStatus = Literal[
    "active",
    "paused",
    "completed",
    "failed",
]
DigitalWorkerRunStatus = Literal["queued", "running", "completed", "failed", "skipped"]
DigitalWorkerTrigger = Literal[
    "assignment_created",
    "inbound_email",
    "follow_up_due",
    "manual_resume",
]
DigitalWorkerGoalStatus = Literal["pending", "completed", "skipped"]
DigitalWorkerMessageDirection = Literal["inbound", "outbound"]
DigitalWorkerMessageChannel = Literal["email"]
DigitalWorkerFollowUpStatus = Literal[
    "pending",
    "claimed",
    "completed",
    "cancelled",
]


class DigitalWorkerAssignmentCreate(BaseModel):
    lead_id: UUID = Field(description="Completed lead id to assign to the worker.")


class DigitalWorkerInboundEmailCreate(BaseModel):
    external_message_id: str | None = Field(
        default=None,
        max_length=180,
        description="Optional upstream sandbox message id for idempotent display.",
    )
    received_at: datetime | None = Field(
        default=None,
        description="When the inbound sandbox email was received.",
    )
    subject: str = Field(
        min_length=1,
        max_length=240,
        description="Inbound sandbox email subject.",
    )
    body: str = Field(
        min_length=1,
        max_length=12000,
        description="Inbound sandbox email body stored for worker context.",
    )


class DigitalWorkerGoalStateResponse(BaseModel):
    phase_key: str
    goal_key: str
    status: DigitalWorkerGoalStatus
    completed_at: datetime | None = None
    notes: str | None = None


class DigitalWorkerMessageResponse(BaseModel):
    message_id: UUID
    assignment_id: UUID
    direction: DigitalWorkerMessageDirection
    channel: DigitalWorkerMessageChannel = "email"
    subject: str
    body: str
    external_message_id: str | None = None
    created_at: datetime | None = None


class DigitalWorkerFollowUpResponse(BaseModel):
    follow_up_id: UUID
    assignment_id: UUID
    status: DigitalWorkerFollowUpStatus
    due_at: datetime
    reason: str
    claimed_run_id: UUID | None = None
    created_at: datetime | None = None


class DigitalWorkerRunResponse(BaseModel):
    run_id: UUID
    assignment_id: UUID
    trigger: DigitalWorkerTrigger
    status: DigitalWorkerRunStatus
    current_phase: str
    message: str | None = None
    created_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failed_at: datetime | None = None


class DigitalWorkerAssignmentResponse(BaseModel):
    assignment_id: UUID
    lead_id: UUID
    status: DigitalWorkerAssignmentStatus
    current_phase: str
    lifecycle_version: str
    latest_run_id: UUID | None = None
    activity_log: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    goals: list[DigitalWorkerGoalStateResponse] = Field(default_factory=list)
    messages: list[DigitalWorkerMessageResponse] = Field(default_factory=list)
    follow_ups: list[DigitalWorkerFollowUpResponse] = Field(default_factory=list)
    runs: list[DigitalWorkerRunResponse] = Field(default_factory=list)
