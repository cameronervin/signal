from typing import Literal

from pydantic import BaseModel, Field

RunStatus = Literal["queued", "running", "awaiting_review", "completed", "failed"]
StepStatus = Literal["pending", "running", "done", "failed", "skipped"]
RunStage = Literal[
    "received",
    "enrichment",
    "scoring",
    "knowledge_graph",
    "human_review",
    "gate_failed",
    "completed",
]


class AgentStep(BaseModel):
    name: str
    status: StepStatus
    summary: str
    duration_ms: int | None = None


class AgentRunResponse(BaseModel):
    run_id: str
    lead_id: str
    status: RunStatus
    trigger: str = "api_insert"
    current_stage: RunStage
    stage_index: int
    steps: list[AgentStep] = Field(default_factory=list)
    activity_log: list[str] = Field(default_factory=list)
    degraded_reasons: list[str] = Field(default_factory=list)
