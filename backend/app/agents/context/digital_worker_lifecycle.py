from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field


class LifecycleGoal(BaseModel):
    key: str
    description: str
    example_actions: list[str] = Field(default_factory=list)


class LifecyclePhase(BaseModel):
    key: str
    label: str
    done_when: str
    goals: list[LifecycleGoal]


class DigitalWorkerLifecycleSpec(BaseModel):
    version: str
    initial_phase: str
    default_follow_up_delay_minutes: int = Field(ge=1)
    phases: list[LifecyclePhase]

    def phase(self, key: str) -> LifecyclePhase:
        for phase in self.phases:
            if phase.key == key:
                return phase
        raise KeyError(key)

    def next_phase_key(self, key: str) -> str:
        for index, phase in enumerate(self.phases):
            if phase.key == key:
                next_index = min(index + 1, len(self.phases) - 1)
                return self.phases[next_index].key
        raise KeyError(key)


DEFAULT_LIFECYCLE_SPEC_PATH = (
    Path(__file__).parent / "lifecycle_specs" / "qualify_to_meeting.v1.json"
)


@lru_cache
def load_default_lifecycle_spec() -> DigitalWorkerLifecycleSpec:
    return DigitalWorkerLifecycleSpec.model_validate_json(
        DEFAULT_LIFECYCLE_SPEC_PATH.read_text(encoding="utf-8")
    )
