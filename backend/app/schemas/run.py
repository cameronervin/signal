from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

RunStatus = Literal[
    "queued",
    "running",
    "awaiting_review",
    "paused",
    "completed",
    "failed",
]
StepStatus = Literal["pending", "running", "done", "failed", "skipped"]


class AgentStep(BaseModel):
    name: str
    status: StepStatus
    summary: str
    duration_ms: int | None = None


class AgentRunResponse(BaseModel):
    run_id: UUID
    lead_id: UUID
    status: RunStatus
    trigger: str = "api_insert"
    current_stage: str
    steps: list[AgentStep] = Field(default_factory=list)
    activity_log: list[str] = Field(default_factory=list)


class AgentRunStatusEvent(BaseModel):
    id: UUID
    run_id: UUID
    status: RunStatus
    current_stage: str
    message: str | None = None
    payload: dict[str, object] | None = None
