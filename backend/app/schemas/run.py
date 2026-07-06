from typing import Literal

from pydantic import BaseModel, Field

RunStatus = Literal["queued", "running", "awaiting_review", "completed", "failed"]
StepStatus = Literal["pending", "running", "done", "failed", "skipped"]
ExecutionMode = Literal["inline", "eager", "worker"]


class AgentStep(BaseModel):
    stage: str
    name: str
    status: StepStatus
    summary: str
    duration_ms: int | None = None


class AgentRunResponse(BaseModel):
    run_id: str
    lead_id: str
    status: RunStatus
    trigger: str = "api_insert"
    execution_mode: ExecutionMode = "inline"
    task_id: str | None = None
    worker_queue: str | None = None
    current_stage: str
    steps: list[AgentStep] = Field(default_factory=list)
    activity_log: list[str] = Field(default_factory=list)
    degraded_reasons: list[str] = Field(default_factory=list)
