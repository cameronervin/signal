"""Add SDR digital worker runtime tables.

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-08 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "digital_worker_assignments",
        sa.Column("assignment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("current_phase", sa.String(length=80), nullable=False),
        sa.Column("lifecycle_version", sa.String(length=80), nullable=False),
        sa.Column("latest_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("assignment_id"),
    )
    op.create_index(
        "ix_digital_worker_assignments_current_phase",
        "digital_worker_assignments",
        ["current_phase"],
    )
    op.create_index(
        "ix_digital_worker_assignments_latest_run_id",
        "digital_worker_assignments",
        ["latest_run_id"],
    )
    op.create_index(
        "ix_digital_worker_assignments_lead_id",
        "digital_worker_assignments",
        ["lead_id"],
    )
    op.create_index(
        "ix_digital_worker_assignments_lifecycle_version",
        "digital_worker_assignments",
        ["lifecycle_version"],
    )
    op.create_index(
        "ix_digital_worker_assignments_status",
        "digital_worker_assignments",
        ["status"],
    )

    op.create_table(
        "digital_worker_runs",
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assignment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trigger", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("current_phase", sa.String(length=80), nullable=False),
        sa.Column("message", sa.String(length=240), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["assignment_id"],
            ["digital_worker_assignments.assignment_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("run_id"),
    )
    op.create_index(
        "ix_digital_worker_runs_assignment_id",
        "digital_worker_runs",
        ["assignment_id"],
    )
    op.create_index(
        "ix_digital_worker_runs_current_phase",
        "digital_worker_runs",
        ["current_phase"],
    )
    op.create_index("ix_digital_worker_runs_status", "digital_worker_runs", ["status"])
    op.create_index(
        "ix_digital_worker_runs_trigger",
        "digital_worker_runs",
        ["trigger"],
    )

    op.create_table(
        "digital_worker_goal_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assignment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phase_key", sa.String(length=80), nullable=False),
        sa.Column("goal_key", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.String(length=240), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["assignment_id"],
            ["digital_worker_assignments.assignment_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_digital_worker_goal_states_assignment_id",
        "digital_worker_goal_states",
        ["assignment_id"],
    )
    op.create_index(
        "ix_digital_worker_goal_states_goal_key",
        "digital_worker_goal_states",
        ["goal_key"],
    )
    op.create_index(
        "ix_digital_worker_goal_states_phase_key",
        "digital_worker_goal_states",
        ["phase_key"],
    )
    op.create_index(
        "ix_digital_worker_goal_states_status",
        "digital_worker_goal_states",
        ["status"],
    )
    op.create_unique_constraint(
        "uq_digital_worker_goal_assignment_phase_goal",
        "digital_worker_goal_states",
        ["assignment_id", "phase_key", "goal_key"],
    )

    op.create_table(
        "digital_worker_messages",
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assignment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("subject", sa.String(length=240), nullable=False),
        sa.Column("body", sa.String(), nullable=False),
        sa.Column("external_message_id", sa.String(length=180), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["assignment_id"],
            ["digital_worker_assignments.assignment_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("message_id"),
    )
    op.create_index(
        "ix_digital_worker_messages_assignment_id",
        "digital_worker_messages",
        ["assignment_id"],
    )
    op.create_index(
        "ix_digital_worker_messages_channel",
        "digital_worker_messages",
        ["channel"],
    )
    op.create_index(
        "ix_digital_worker_messages_direction",
        "digital_worker_messages",
        ["direction"],
    )
    op.create_index(
        "ix_digital_worker_messages_external_message_id",
        "digital_worker_messages",
        ["external_message_id"],
    )

    op.create_table(
        "digital_worker_follow_ups",
        sa.Column("follow_up_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assignment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(length=240), nullable=False),
        sa.Column("claimed_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["assignment_id"],
            ["digital_worker_assignments.assignment_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("follow_up_id"),
    )
    op.create_index(
        "ix_digital_worker_follow_ups_assignment_id",
        "digital_worker_follow_ups",
        ["assignment_id"],
    )
    op.create_index(
        "ix_digital_worker_follow_ups_claimed_run_id",
        "digital_worker_follow_ups",
        ["claimed_run_id"],
    )
    op.create_index(
        "ix_digital_worker_follow_ups_due_at",
        "digital_worker_follow_ups",
        ["due_at"],
    )
    op.create_index(
        "ix_digital_worker_follow_ups_status",
        "digital_worker_follow_ups",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_digital_worker_follow_ups_status",
        table_name="digital_worker_follow_ups",
    )
    op.drop_index(
        "ix_digital_worker_follow_ups_due_at",
        table_name="digital_worker_follow_ups",
    )
    op.drop_index(
        "ix_digital_worker_follow_ups_claimed_run_id",
        table_name="digital_worker_follow_ups",
    )
    op.drop_index(
        "ix_digital_worker_follow_ups_assignment_id",
        table_name="digital_worker_follow_ups",
    )
    op.drop_table("digital_worker_follow_ups")

    op.drop_index(
        "ix_digital_worker_messages_external_message_id",
        table_name="digital_worker_messages",
    )
    op.drop_index(
        "ix_digital_worker_messages_direction",
        table_name="digital_worker_messages",
    )
    op.drop_index(
        "ix_digital_worker_messages_channel",
        table_name="digital_worker_messages",
    )
    op.drop_index(
        "ix_digital_worker_messages_assignment_id",
        table_name="digital_worker_messages",
    )
    op.drop_table("digital_worker_messages")

    op.drop_constraint(
        "uq_digital_worker_goal_assignment_phase_goal",
        "digital_worker_goal_states",
        type_="unique",
    )
    op.drop_index(
        "ix_digital_worker_goal_states_status",
        table_name="digital_worker_goal_states",
    )
    op.drop_index(
        "ix_digital_worker_goal_states_phase_key",
        table_name="digital_worker_goal_states",
    )
    op.drop_index(
        "ix_digital_worker_goal_states_goal_key",
        table_name="digital_worker_goal_states",
    )
    op.drop_index(
        "ix_digital_worker_goal_states_assignment_id",
        table_name="digital_worker_goal_states",
    )
    op.drop_table("digital_worker_goal_states")

    op.drop_index("ix_digital_worker_runs_trigger", table_name="digital_worker_runs")
    op.drop_index("ix_digital_worker_runs_status", table_name="digital_worker_runs")
    op.drop_index(
        "ix_digital_worker_runs_current_phase",
        table_name="digital_worker_runs",
    )
    op.drop_index(
        "ix_digital_worker_runs_assignment_id",
        table_name="digital_worker_runs",
    )
    op.drop_table("digital_worker_runs")

    op.drop_index(
        "ix_digital_worker_assignments_status",
        table_name="digital_worker_assignments",
    )
    op.drop_index(
        "ix_digital_worker_assignments_lifecycle_version",
        table_name="digital_worker_assignments",
    )
    op.drop_index(
        "ix_digital_worker_assignments_lead_id",
        table_name="digital_worker_assignments",
    )
    op.drop_index(
        "ix_digital_worker_assignments_latest_run_id",
        table_name="digital_worker_assignments",
    )
    op.drop_index(
        "ix_digital_worker_assignments_current_phase",
        table_name="digital_worker_assignments",
    )
    op.drop_table("digital_worker_assignments")
