"""Policy chain for the SDR Digital Worker agent."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field

from app.agents.context.digital_worker_lifecycle import DigitalWorkerLifecycleSpec
from app.agents.prompts.digital_worker import (
    DIGITAL_WORKER_SYSTEM_PROMPT,
    digital_worker_tool_prompt,
)
from app.agents.tools.digital_worker import (
    DIGITAL_WORKER_MARK_GOAL_COMPLETE_TOOL,
    DIGITAL_WORKER_MARK_PHASE_OUTCOME_TOOL,
    DIGITAL_WORKER_SCHEDULE_FOLLOW_UP_TOOL,
    DIGITAL_WORKER_SEND_SANDBOX_EMAIL_TOOL,
)
from app.core.config import Settings
from app.schemas.digital_worker import (
    DigitalWorkerAssignmentResponse,
    DigitalWorkerTrigger,
)
from app.schemas.lead import LeadResponse

DIGITAL_WORKER_DECISION_CHAIN = "digital_worker_decision"


class DigitalWorkerPlannedAction(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class DigitalWorkerDecision(BaseModel):
    trigger: DigitalWorkerTrigger
    actions: list[DigitalWorkerPlannedAction] = Field(default_factory=list)
    activity: str


class DigitalWorkerDecisionChain:
    """Bounded lifecycle policy for one Digital Worker graph wake-up."""

    def __init__(self, *, settings: Settings) -> None:
        self.settings = settings
        self.instructions = "\n".join(
            [DIGITAL_WORKER_SYSTEM_PROMPT.strip(), digital_worker_tool_prompt()]
        )

    async def ainvoke(
        self,
        input: dict[str, Any],
        *,
        config: dict[str, object] | None = None,
        context: object | None = None,
    ) -> DigitalWorkerDecision:
        assignment = input["assignment"]
        lead = input["lead"]
        lifecycle = input["lifecycle"]
        trigger = input["trigger"]
        if (
            not isinstance(assignment, DigitalWorkerAssignmentResponse)
            or not isinstance(lead, LeadResponse)
            or not isinstance(lifecycle, DigitalWorkerLifecycleSpec)
            or trigger
            not in {
                "assignment_created",
                "inbound_email",
                "follow_up_due",
                "manual_resume",
            }
        ):
            raise TypeError(
                "Digital Worker decision chain received invalid input types"
            )

        if trigger == "assignment_created":
            return _initial_assignment_decision(
                assignment=assignment,
                lead=lead,
                lifecycle=lifecycle,
            )
        if trigger == "inbound_email":
            return _inbound_email_decision(
                assignment=assignment,
                lifecycle=lifecycle,
            )
        return _follow_up_due_decision(
            assignment=assignment,
            lifecycle=lifecycle,
            trigger=trigger,
        )


def create_digital_worker_decision_chain(
    *,
    settings: Settings,
) -> DigitalWorkerDecisionChain:
    return DigitalWorkerDecisionChain(settings=settings)


def _initial_assignment_decision(
    *,
    assignment: DigitalWorkerAssignmentResponse,
    lead: LeadResponse,
    lifecycle: DigitalWorkerLifecycleSpec,
) -> DigitalWorkerDecision:
    if any(message.direction == "outbound" for message in assignment.messages):
        return DigitalWorkerDecision(
            trigger="assignment_created",
            actions=[
                _action(
                    DIGITAL_WORKER_MARK_PHASE_OUTCOME_TOOL,
                    assignment_id=assignment.assignment_id,
                    activity="initial_outreach: sandbox draft already sent",
                )
            ],
            activity="initial assignment already had outbound communication",
        )
    if lead.draft is None:
        raise ValueError("Assigned lead draft is missing")

    phase_key = "initial_outreach"
    return DigitalWorkerDecision(
        trigger="assignment_created",
        actions=[
            _action(
                DIGITAL_WORKER_SEND_SANDBOX_EMAIL_TOOL,
                assignment_id=assignment.assignment_id,
                subject=lead.draft.subject,
                body=lead.draft.body,
            ),
            _action(
                DIGITAL_WORKER_MARK_GOAL_COMPLETE_TOOL,
                assignment_id=assignment.assignment_id,
                phase_key=phase_key,
                goal_key="send_existing_draft",
                notes="Existing lead-intelligence draft sent through sandbox email.",
            ),
            _action(
                DIGITAL_WORKER_SCHEDULE_FOLLOW_UP_TOOL,
                assignment_id=assignment.assignment_id,
                due_at=_follow_up_due_at(lifecycle),
                reason="first follow-up after initial sandbox email",
            ),
            _action(
                DIGITAL_WORKER_MARK_GOAL_COMPLETE_TOOL,
                assignment_id=assignment.assignment_id,
                phase_key=phase_key,
                goal_key="schedule_first_follow_up",
                notes="First follow-up scheduled from lifecycle defaults.",
            ),
            _action(
                DIGITAL_WORKER_MARK_PHASE_OUTCOME_TOOL,
                assignment_id=assignment.assignment_id,
                current_phase=lifecycle.next_phase_key(phase_key),
                activity="phase: moved to reply qualification",
            ),
        ],
        activity="initial assignment outreach planned",
    )


def _inbound_email_decision(
    *,
    assignment: DigitalWorkerAssignmentResponse,
    lifecycle: DigitalWorkerLifecycleSpec,
) -> DigitalWorkerDecision:
    latest_inbound = next(
        (
            message
            for message in reversed(assignment.messages)
            if message.direction == "inbound"
        ),
        None,
    )
    body = (latest_inbound.body if latest_inbound else "").lower()
    actions = [
        _action(
            DIGITAL_WORKER_MARK_GOAL_COMPLETE_TOOL,
            assignment_id=assignment.assignment_id,
            phase_key="reply_qualification",
            goal_key="capture_reply",
            notes="Inbound sandbox email captured.",
        ),
        _action(
            DIGITAL_WORKER_MARK_GOAL_COMPLETE_TOOL,
            assignment_id=assignment.assignment_id,
            phase_key="reply_qualification",
            goal_key="classify_intent",
            notes="Reply classified by deterministic v1 rules.",
        ),
    ]
    if _looks_meeting_ready(body):
        return DigitalWorkerDecision(
            trigger="inbound_email",
            actions=[
                *actions,
                _action(
                    DIGITAL_WORKER_MARK_GOAL_COMPLETE_TOOL,
                    assignment_id=assignment.assignment_id,
                    phase_key="meeting_handoff",
                    goal_key="mark_meeting_ready",
                    notes="Reply indicates meeting-ready intent.",
                ),
                _action(
                    DIGITAL_WORKER_MARK_PHASE_OUTCOME_TOOL,
                    assignment_id=assignment.assignment_id,
                    status="completed",
                    current_phase="meeting_handoff",
                    activity="outcome: meeting-ready handoff",
                ),
            ],
            activity="inbound reply classified as meeting ready",
        )
    if _looks_disqualified(body):
        return DigitalWorkerDecision(
            trigger="inbound_email",
            actions=[
                *actions,
                _action(
                    DIGITAL_WORKER_MARK_PHASE_OUTCOME_TOOL,
                    assignment_id=assignment.assignment_id,
                    status="completed",
                    current_phase="closed_outcome",
                    activity="outcome: disqualified or not interested",
                ),
            ],
            activity="inbound reply classified as closed",
        )
    return DigitalWorkerDecision(
        trigger="inbound_email",
        actions=[
            *actions,
            _action(
                DIGITAL_WORKER_SCHEDULE_FOLLOW_UP_TOOL,
                assignment_id=assignment.assignment_id,
                due_at=_follow_up_due_at(lifecycle),
                reason="follow-up after non-terminal inbound reply",
            ),
            _action(
                DIGITAL_WORKER_MARK_PHASE_OUTCOME_TOOL,
                assignment_id=assignment.assignment_id,
                current_phase="objection_or_follow_up",
                activity="phase: moved to objection or follow-up",
            ),
        ],
        activity="inbound reply needs follow-up",
    )


def _follow_up_due_decision(
    *,
    assignment: DigitalWorkerAssignmentResponse,
    lifecycle: DigitalWorkerLifecycleSpec,
    trigger: DigitalWorkerTrigger,
) -> DigitalWorkerDecision:
    outbound_count = sum(
        1 for message in assignment.messages if message.direction == "outbound"
    )
    if outbound_count >= 2:
        return DigitalWorkerDecision(
            trigger=trigger,
            actions=[
                _action(
                    DIGITAL_WORKER_MARK_PHASE_OUTCOME_TOOL,
                    assignment_id=assignment.assignment_id,
                    status="completed",
                    current_phase="closed_outcome",
                    activity="outcome: no response after sandbox follow-up",
                )
            ],
            activity="follow-up sequence completed without response",
        )

    return DigitalWorkerDecision(
        trigger=trigger,
        actions=[
            _action(
                DIGITAL_WORKER_SEND_SANDBOX_EMAIL_TOOL,
                assignment_id=assignment.assignment_id,
                subject="Following up",
                body=(
                    "Hi, I wanted to follow up on my earlier note. "
                    "Would it be useful to compare how your team is handling "
                    "inbound leasing demand today?"
                ),
            ),
            _action(
                DIGITAL_WORKER_MARK_GOAL_COMPLETE_TOOL,
                assignment_id=assignment.assignment_id,
                phase_key="objection_or_follow_up",
                goal_key="respond_or_wait",
                notes="Sandbox follow-up email sent.",
            ),
            _action(
                DIGITAL_WORKER_SCHEDULE_FOLLOW_UP_TOOL,
                assignment_id=assignment.assignment_id,
                due_at=_follow_up_due_at(lifecycle),
                reason="second follow-up after sandbox email",
            ),
            _action(
                DIGITAL_WORKER_MARK_PHASE_OUTCOME_TOOL,
                assignment_id=assignment.assignment_id,
                current_phase="objection_or_follow_up",
                activity="follow_up: sandbox email sent",
            ),
        ],
        activity="follow-up email planned",
    )


def _action(tool_name: str, **arguments: Any) -> DigitalWorkerPlannedAction:
    return DigitalWorkerPlannedAction(tool_name=tool_name, arguments=arguments)


def _follow_up_due_at(lifecycle: DigitalWorkerLifecycleSpec) -> datetime:
    return datetime.now(UTC) + timedelta(
        minutes=lifecycle.default_follow_up_delay_minutes
    )


def _looks_meeting_ready(body: str) -> bool:
    return any(
        token in body
        for token in ("schedule", "meeting", "call", "demo", "next week")
    )


def _looks_disqualified(body: str) -> bool:
    return any(token in body for token in ("not interested", "unsubscribe", "stop"))
