from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class SignalLeadRecord(Base):
    __tablename__ = "signal_leads"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(64), index=True)
    tier: Mapped[str] = mapped_column(String(1), index=True)
    score_total: Mapped[int] = mapped_column(Integer, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())


class SignalAgentRunRecord(Base):
    __tablename__ = "signal_agent_runs"

    run_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    lead_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    current_stage: Mapped[str] = mapped_column(String(80), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
