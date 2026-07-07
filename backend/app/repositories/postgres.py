from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.signal import SignalAgentRunRecord, SignalLeadRecord
from app.schemas.lead import LeadResponse
from app.schemas.run import AgentRunResponse

TIER_SORT = {"A": 0, "B": 1, "C": 2}


class PostgresSignalRepository:
    """Postgres persistence boundary for Signal DTO snapshots.

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
            payload=lead.model_dump(mode="json"),
        )
        await self.session.merge(record)

    async def list_leads(self) -> list[LeadResponse]:
        result = await self.session.scalars(select(SignalLeadRecord))
        leads = [LeadResponse.model_validate(record.payload) for record in result]
        return sorted(
            leads,
            key=lambda lead: (TIER_SORT[lead.score.tier], -lead.score.total),
        )

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
            payload=run.model_dump(mode="json"),
        )
        await self.session.merge(record)

    async def list_agent_runs(self) -> list[AgentRunResponse]:
        result = await self.session.scalars(select(SignalAgentRunRecord))
        return [AgentRunResponse.model_validate(record.payload) for record in result]

    async def get_agent_run(self, run_id: str) -> AgentRunResponse | None:
        record = await self.session.get(SignalAgentRunRecord, run_id)
        if record is None:
            return None
        return AgentRunResponse.model_validate(record.payload)

    async def commit(self) -> None:
        await self.session.commit()
