from typing import Protocol

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.signal import SignalAgentRunRecord, SignalLeadRecord
from app.schemas.analytics import AnalyticsSummaryResponse, MarketSummary
from app.schemas.lead import LeadResponse
from app.schemas.run import AgentRunResponse

TIER_SORT = {"A": 0, "B": 1, "C": 2}


class SignalRepository(Protocol):
    async def save_lead(self, lead: LeadResponse) -> None: ...

    async def list_leads(self) -> list[LeadResponse]: ...

    async def get_lead(self, lead_id: str) -> LeadResponse | None: ...

    async def save_agent_run(self, run: AgentRunResponse) -> None: ...

    async def list_agent_runs(self) -> list[AgentRunResponse]: ...

    async def get_agent_run(self, run_id: str) -> AgentRunResponse | None: ...

    async def analytics_summary(self) -> AnalyticsSummaryResponse: ...


class SignalSnapshotRepository:
    """Persistence boundary for Signal lead and run DTO snapshots.

    V1 stores API response DTO payloads as JSON while indexing fields needed for
    queue sorting and run polling. That keeps the contract stable while the data
    model matures toward fuller relational tables.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_lead(self, lead: LeadResponse) -> None:
        record = SignalLeadRecord(
            id=lead.id,
            run_id=lead.run_id,
            tier=lead.score.tier,
            score_total=lead.score.total,
            market=lead.enrichment.market,
            gate_status=lead.gates.status,
            payload=lead.model_dump(mode="json"),
        )
        await self.session.merge(record)

    async def list_leads(self) -> list[LeadResponse]:
        tier_order = case(
            (SignalLeadRecord.tier == "A", TIER_SORT["A"]),
            (SignalLeadRecord.tier == "B", TIER_SORT["B"]),
            else_=TIER_SORT["C"],
        )
        result = await self.session.scalars(
            select(SignalLeadRecord).order_by(
                tier_order.asc(),
                SignalLeadRecord.score_total.desc(),
                SignalLeadRecord.created_at.asc(),
            )
        )
        return [LeadResponse.model_validate(record.payload) for record in result]

    async def get_lead(self, lead_id: str) -> LeadResponse | None:
        record = await self.session.get(SignalLeadRecord, lead_id)
        if record is None:
            return None
        return LeadResponse.model_validate(record.payload)

    async def save_agent_run(self, run: AgentRunResponse) -> None:
        record = SignalAgentRunRecord(
            run_id=run.run_id,
            lead_id=run.lead_id,
            status=run.status,
            current_stage=run.current_stage,
            trigger=run.trigger,
            payload=run.model_dump(mode="json"),
        )
        await self.session.merge(record)

    async def list_agent_runs(self) -> list[AgentRunResponse]:
        result = await self.session.scalars(
            select(SignalAgentRunRecord).order_by(
                SignalAgentRunRecord.created_at.asc()
            )
        )
        return [AgentRunResponse.model_validate(record.payload) for record in result]

    async def get_agent_run(self, run_id: str) -> AgentRunResponse | None:
        record = await self.session.get(SignalAgentRunRecord, run_id)
        if record is None:
            return None
        return AgentRunResponse.model_validate(record.payload)

    async def analytics_summary(self) -> AnalyticsSummaryResponse:
        total_leads = await self.session.scalar(
            select(func.count()).select_from(SignalLeadRecord)
        )
        average_score = await self.session.scalar(
            select(func.avg(SignalLeadRecord.score_total))
        )
        tier_counts = await self.session.execute(
            select(SignalLeadRecord.tier, func.count())
            .group_by(SignalLeadRecord.tier)
        )
        awaiting_review_count = await self.session.scalar(
            select(func.count())
            .select_from(SignalAgentRunRecord)
            .where(SignalAgentRunRecord.status == "awaiting_review")
        )
        gate_failed_count = await self.session.scalar(
            select(func.count())
            .select_from(SignalLeadRecord)
            .where(SignalLeadRecord.gate_status == "failed")
        )
        market_counts = await self.session.execute(
            select(SignalLeadRecord.market, func.count().label("lead_count"))
            .where(SignalLeadRecord.market.is_not(None))
            .group_by(SignalLeadRecord.market)
            .order_by(func.count().desc(), SignalLeadRecord.market.asc())
            .limit(5)
        )

        tier_distribution = {"A": 0, "B": 0, "C": 0}
        for tier, count in tier_counts:
            if tier in tier_distribution:
                tier_distribution[tier] = count

        return AnalyticsSummaryResponse(
            total_leads=total_leads or 0,
            tier_distribution=tier_distribution,
            awaiting_review_count=awaiting_review_count or 0,
            gate_failed_count=gate_failed_count or 0,
            average_score=round(float(average_score), 1) if average_score else 0.0,
            top_markets=[
                MarketSummary(market=market, lead_count=count)
                for market, count in market_counts
                if market is not None
            ],
        )
