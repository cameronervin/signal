"""Add query fields to Signal snapshots.

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-07 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "signal_leads",
        sa.Column("market", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "signal_leads",
        sa.Column("gate_status", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "signal_leads",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_signal_leads_gate_status",
        "signal_leads",
        ["gate_status"],
        unique=False,
    )
    op.create_index(
        "ix_signal_leads_market",
        "signal_leads",
        ["market"],
        unique=False,
    )

    op.add_column(
        "signal_agent_runs",
        sa.Column("trigger", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "signal_agent_runs",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_signal_agent_runs_trigger",
        "signal_agent_runs",
        ["trigger"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_signal_agent_runs_trigger", table_name="signal_agent_runs")
    op.drop_column("signal_agent_runs", "updated_at")
    op.drop_column("signal_agent_runs", "trigger")

    op.drop_index("ix_signal_leads_market", table_name="signal_leads")
    op.drop_index("ix_signal_leads_gate_status", table_name="signal_leads")
    op.drop_column("signal_leads", "updated_at")
    op.drop_column("signal_leads", "gate_status")
    op.drop_column("signal_leads", "market")
