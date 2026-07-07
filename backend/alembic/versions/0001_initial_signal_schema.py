"""Initial Signal schema.

Revision ID: 0001
Revises: None
Create Date: 2026-07-07 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "signal_leads",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("tier", sa.String(length=1), nullable=False),
        sa.Column("score_total", sa.Integer(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_signal_leads_run_id",
        "signal_leads",
        ["run_id"],
        unique=False,
    )
    op.create_index(
        "ix_signal_leads_score_total",
        "signal_leads",
        ["score_total"],
        unique=False,
    )
    op.create_index(
        "ix_signal_leads_tier",
        "signal_leads",
        ["tier"],
        unique=False,
    )

    op.create_table(
        "signal_agent_runs",
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("lead_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("current_stage", sa.String(length=80), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("run_id"),
    )
    op.create_index(
        "ix_signal_agent_runs_current_stage",
        "signal_agent_runs",
        ["current_stage"],
        unique=False,
    )
    op.create_index(
        "ix_signal_agent_runs_lead_id",
        "signal_agent_runs",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_signal_agent_runs_status",
        "signal_agent_runs",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_signal_agent_runs_status", table_name="signal_agent_runs")
    op.drop_index("ix_signal_agent_runs_lead_id", table_name="signal_agent_runs")
    op.drop_index(
        "ix_signal_agent_runs_current_stage",
        table_name="signal_agent_runs",
    )
    op.drop_table("signal_agent_runs")

    op.drop_index("ix_signal_leads_tier", table_name="signal_leads")
    op.drop_index("ix_signal_leads_score_total", table_name="signal_leads")
    op.drop_index("ix_signal_leads_run_id", table_name="signal_leads")
    op.drop_table("signal_leads")
