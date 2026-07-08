"""Use UUIDs and queued agent run lifecycle fields.

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-07 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute(
        """
        CREATE TEMP TABLE signal_uuid_migration_map AS
        SELECT
            old_lead_id,
            gen_random_uuid() AS new_lead_id,
            old_run_id,
            gen_random_uuid() AS new_run_id
        FROM (
            SELECT id AS old_lead_id, run_id AS old_run_id
            FROM signal_leads
            UNION
            SELECT lead_id AS old_lead_id, run_id AS old_run_id
            FROM signal_agent_runs
        ) mapped
        WHERE old_lead_id IS NOT NULL AND old_run_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE signal_leads AS l
        SET payload = jsonb_set(
            jsonb_set(l.payload::jsonb, '{id}', to_jsonb(m.new_lead_id::text)),
            '{run_id}',
            to_jsonb(m.new_run_id::text)
        )::json
        FROM signal_uuid_migration_map AS m
        WHERE l.id = m.old_lead_id OR l.run_id = m.old_run_id
        """
    )
    op.execute(
        """
        UPDATE signal_agent_runs AS r
        SET payload = jsonb_set(
            jsonb_set(r.payload::jsonb, '{lead_id}', to_jsonb(m.new_lead_id::text)),
            '{run_id}',
            to_jsonb(m.new_run_id::text)
        )::json
        FROM signal_uuid_migration_map AS m
        WHERE r.lead_id = m.old_lead_id OR r.run_id = m.old_run_id
        """
    )

    op.add_column(
        "signal_leads",
        sa.Column("id_uuid", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "signal_leads",
        sa.Column("run_id_uuid", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute(
        """
        UPDATE signal_leads AS l
        SET id_uuid = m.new_lead_id,
            run_id_uuid = m.new_run_id
        FROM signal_uuid_migration_map AS m
        WHERE l.id = m.old_lead_id OR l.run_id = m.old_run_id
        """
    )
    op.drop_index("ix_signal_leads_gate_status", table_name="signal_leads")
    op.drop_index("ix_signal_leads_market", table_name="signal_leads")
    op.drop_index("ix_signal_leads_run_id", table_name="signal_leads")
    op.drop_index("ix_signal_leads_score_total", table_name="signal_leads")
    op.drop_index("ix_signal_leads_tier", table_name="signal_leads")
    op.drop_constraint("signal_leads_pkey", "signal_leads", type_="primary")
    op.drop_column("signal_leads", "id")
    op.drop_column("signal_leads", "run_id")
    op.alter_column("signal_leads", "id_uuid", new_column_name="id")
    op.alter_column("signal_leads", "run_id_uuid", new_column_name="run_id")
    op.alter_column("signal_leads", "id", nullable=False)
    op.alter_column("signal_leads", "run_id", nullable=False)
    op.create_primary_key("signal_leads_pkey", "signal_leads", ["id"])
    op.create_index("ix_signal_leads_gate_status", "signal_leads", ["gate_status"])
    op.create_index("ix_signal_leads_market", "signal_leads", ["market"])
    op.create_index("ix_signal_leads_run_id", "signal_leads", ["run_id"])
    op.create_index("ix_signal_leads_score_total", "signal_leads", ["score_total"])
    op.create_index("ix_signal_leads_tier", "signal_leads", ["tier"])

    op.add_column(
        "signal_agent_runs",
        sa.Column("run_id_uuid", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "signal_agent_runs",
        sa.Column("lead_id_uuid", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "signal_agent_runs",
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "signal_agent_runs",
        sa.Column("input_payload", sa.JSON(), nullable=True),
    )
    op.add_column(
        "signal_agent_runs",
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "signal_agent_runs",
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "signal_agent_runs",
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        """
        UPDATE signal_agent_runs AS r
        SET run_id_uuid = m.new_run_id,
            lead_id_uuid = m.new_lead_id,
            task_id = m.new_run_id,
            completed_at = CASE
                WHEN r.status IN ('awaiting_review', 'completed') THEN r.updated_at
                ELSE NULL
            END,
            failed_at = CASE WHEN r.status = 'failed' THEN r.updated_at ELSE NULL END
        FROM signal_uuid_migration_map AS m
        WHERE r.lead_id = m.old_lead_id OR r.run_id = m.old_run_id
        """
    )
    op.drop_index("ix_signal_agent_runs_current_stage", table_name="signal_agent_runs")
    op.drop_index("ix_signal_agent_runs_lead_id", table_name="signal_agent_runs")
    op.drop_index("ix_signal_agent_runs_status", table_name="signal_agent_runs")
    op.drop_index("ix_signal_agent_runs_trigger", table_name="signal_agent_runs")
    op.drop_constraint(
        "signal_agent_runs_pkey",
        "signal_agent_runs",
        type_="primary",
    )
    op.drop_column("signal_agent_runs", "run_id")
    op.drop_column("signal_agent_runs", "lead_id")
    op.alter_column("signal_agent_runs", "run_id_uuid", new_column_name="run_id")
    op.alter_column("signal_agent_runs", "lead_id_uuid", new_column_name="lead_id")
    op.alter_column("signal_agent_runs", "run_id", nullable=False)
    op.alter_column("signal_agent_runs", "lead_id", nullable=False)
    op.create_primary_key(
        "signal_agent_runs_pkey",
        "signal_agent_runs",
        ["run_id"],
    )
    op.create_index(
        "ix_signal_agent_runs_current_stage",
        "signal_agent_runs",
        ["current_stage"],
    )
    op.create_index("ix_signal_agent_runs_lead_id", "signal_agent_runs", ["lead_id"])
    op.create_index("ix_signal_agent_runs_status", "signal_agent_runs", ["status"])
    op.create_index("ix_signal_agent_runs_task_id", "signal_agent_runs", ["task_id"])
    op.create_index("ix_signal_agent_runs_trigger", "signal_agent_runs", ["trigger"])

    op.create_table(
        "signal_agent_run_status_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("current_stage", sa.String(length=80), nullable=False),
        sa.Column("message", sa.String(length=240), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["signal_agent_runs.run_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_signal_agent_run_status_events_current_stage",
        "signal_agent_run_status_events",
        ["current_stage"],
    )
    op.create_index(
        "ix_signal_agent_run_status_events_run_id",
        "signal_agent_run_status_events",
        ["run_id"],
    )
    op.create_index(
        "ix_signal_agent_run_status_events_status",
        "signal_agent_run_status_events",
        ["status"],
    )
    op.execute(
        """
        INSERT INTO signal_agent_run_status_events
            (id, run_id, status, current_stage, message, payload, created_at)
        SELECT
            gen_random_uuid(),
            run_id,
            status,
            current_stage,
            'status preserved during UUID migration',
            NULL,
            created_at
        FROM signal_agent_runs
        """
    )


def downgrade() -> None:
    op.drop_index(
        "ix_signal_agent_run_status_events_status",
        table_name="signal_agent_run_status_events",
    )
    op.drop_index(
        "ix_signal_agent_run_status_events_run_id",
        table_name="signal_agent_run_status_events",
    )
    op.drop_index(
        "ix_signal_agent_run_status_events_current_stage",
        table_name="signal_agent_run_status_events",
    )
    op.drop_table("signal_agent_run_status_events")

    op.drop_index("ix_signal_agent_runs_trigger", table_name="signal_agent_runs")
    op.drop_index("ix_signal_agent_runs_task_id", table_name="signal_agent_runs")
    op.drop_index("ix_signal_agent_runs_status", table_name="signal_agent_runs")
    op.drop_index("ix_signal_agent_runs_lead_id", table_name="signal_agent_runs")
    op.drop_index(
        "ix_signal_agent_runs_current_stage",
        table_name="signal_agent_runs",
    )
    op.drop_constraint(
        "signal_agent_runs_pkey",
        "signal_agent_runs",
        type_="primary",
    )
    op.alter_column(
        "signal_agent_runs",
        "run_id",
        type_=sa.String(length=64),
        postgresql_using="run_id::text",
    )
    op.alter_column(
        "signal_agent_runs",
        "lead_id",
        type_=sa.String(length=64),
        postgresql_using="lead_id::text",
    )
    op.create_primary_key(
        "signal_agent_runs_pkey",
        "signal_agent_runs",
        ["run_id"],
    )
    op.drop_column("signal_agent_runs", "failed_at")
    op.drop_column("signal_agent_runs", "completed_at")
    op.drop_column("signal_agent_runs", "started_at")
    op.drop_column("signal_agent_runs", "input_payload")
    op.drop_column("signal_agent_runs", "task_id")
    op.create_index(
        "ix_signal_agent_runs_current_stage",
        "signal_agent_runs",
        ["current_stage"],
    )
    op.create_index("ix_signal_agent_runs_lead_id", "signal_agent_runs", ["lead_id"])
    op.create_index("ix_signal_agent_runs_status", "signal_agent_runs", ["status"])
    op.create_index("ix_signal_agent_runs_trigger", "signal_agent_runs", ["trigger"])

    op.drop_index("ix_signal_leads_tier", table_name="signal_leads")
    op.drop_index("ix_signal_leads_score_total", table_name="signal_leads")
    op.drop_index("ix_signal_leads_run_id", table_name="signal_leads")
    op.drop_index("ix_signal_leads_market", table_name="signal_leads")
    op.drop_index("ix_signal_leads_gate_status", table_name="signal_leads")
    op.drop_constraint("signal_leads_pkey", "signal_leads", type_="primary")
    op.alter_column(
        "signal_leads",
        "id",
        type_=sa.String(length=64),
        postgresql_using="id::text",
    )
    op.alter_column(
        "signal_leads",
        "run_id",
        type_=sa.String(length=64),
        postgresql_using="run_id::text",
    )
    op.create_primary_key("signal_leads_pkey", "signal_leads", ["id"])
    op.create_index("ix_signal_leads_gate_status", "signal_leads", ["gate_status"])
    op.create_index("ix_signal_leads_market", "signal_leads", ["market"])
    op.create_index("ix_signal_leads_run_id", "signal_leads", ["run_id"])
    op.create_index("ix_signal_leads_score_total", "signal_leads", ["score_total"])
    op.create_index("ix_signal_leads_tier", "signal_leads", ["tier"])
