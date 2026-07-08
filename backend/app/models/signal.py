import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class SignalLeadRecord(Base):
    __tablename__ = "signal_leads"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    run_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    tier: Mapped[str] = mapped_column(String(1), index=True)
    score_total: Mapped[int] = mapped_column(Integer, index=True)
    market: Mapped[str | None] = mapped_column(String(120), index=True)
    gate_status: Mapped[str | None] = mapped_column(String(20), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class SignalAgentRunRecord(Base):
    __tablename__ = "signal_agent_runs"

    run_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    lead_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        index=True,
    )
    status: Mapped[str] = mapped_column(String(40), index=True)
    trigger: Mapped[str | None] = mapped_column(String(40), index=True)
    current_stage: Mapped[str] = mapped_column(String(80), index=True)
    input_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    started_at = mapped_column(DateTime(timezone=True))
    completed_at = mapped_column(DateTime(timezone=True))
    failed_at = mapped_column(DateTime(timezone=True))


class SignalAgentRunStatusEventRecord(Base):
    __tablename__ = "signal_agent_run_status_events"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("signal_agent_runs.run_id", ondelete="CASCADE"),
        index=True,
    )
    status: Mapped[str] = mapped_column(String(40), index=True)
    current_stage: Mapped[str] = mapped_column(String(80), index=True)
    message: Mapped[str | None] = mapped_column(String(240))
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())


class DigitalWorkerAssignmentRecord(Base):
    __tablename__ = "digital_worker_assignments"

    assignment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    lead_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    current_phase: Mapped[str] = mapped_column(String(80), index=True)
    lifecycle_version: Mapped[str] = mapped_column(String(80), index=True)
    latest_run_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        index=True,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    completed_at = mapped_column(DateTime(timezone=True))
    failed_at = mapped_column(DateTime(timezone=True))


class DigitalWorkerRunRecord(Base):
    __tablename__ = "digital_worker_runs"

    run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    assignment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("digital_worker_assignments.assignment_id", ondelete="CASCADE"),
        index=True,
    )
    trigger: Mapped[str] = mapped_column(String(40), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    current_phase: Mapped[str] = mapped_column(String(80), index=True)
    message: Mapped[str | None] = mapped_column(String(240))
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at = mapped_column(DateTime(timezone=True))
    completed_at = mapped_column(DateTime(timezone=True))
    failed_at = mapped_column(DateTime(timezone=True))


class DigitalWorkerGoalStateRecord(Base):
    __tablename__ = "digital_worker_goal_states"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    assignment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("digital_worker_assignments.assignment_id", ondelete="CASCADE"),
        index=True,
    )
    phase_key: Mapped[str] = mapped_column(String(80), index=True)
    goal_key: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    notes: Mapped[str | None] = mapped_column(String(240))
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at = mapped_column(DateTime(timezone=True))


class DigitalWorkerMessageRecord(Base):
    __tablename__ = "digital_worker_messages"

    message_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    assignment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("digital_worker_assignments.assignment_id", ondelete="CASCADE"),
        index=True,
    )
    direction: Mapped[str] = mapped_column(String(20), index=True)
    channel: Mapped[str] = mapped_column(String(20), index=True)
    subject: Mapped[str] = mapped_column(String(240))
    body: Mapped[str] = mapped_column(String)
    external_message_id: Mapped[str | None] = mapped_column(String(180), index=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())


class DigitalWorkerFollowUpRecord(Base):
    __tablename__ = "digital_worker_follow_ups"

    follow_up_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    assignment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("digital_worker_assignments.assignment_id", ondelete="CASCADE"),
        index=True,
    )
    status: Mapped[str] = mapped_column(String(40), index=True)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    reason: Mapped[str] = mapped_column(String(240))
    claimed_run_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        index=True,
    )
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at = mapped_column(DateTime(timezone=True))
