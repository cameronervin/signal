from collections import Counter
from uuid import UUID, uuid4

from app.infrastructure.public_data.fixtures import demo_enrichment
from app.schemas.analytics import AnalyticsSummaryResponse, MarketSummary
from app.schemas.lead import LeadCreate, LeadResponse
from app.schemas.run import AgentRunResponse, AgentRunStatusEvent


class FakePublicDataClient:
    def __init__(self) -> None:
        self.calls = 0

    async def enrich(self, lead: LeadCreate):
        self.calls += 1
        return demo_enrichment(lead.company, lead.city, lead.state)


class FakeSignalRepository:
    def __init__(self) -> None:
        self._leads: dict[UUID, LeadResponse] = {}
        self._runs: dict[UUID, AgentRunResponse] = {}
        self._run_inputs: dict[UUID, LeadCreate] = {}
        self._events: dict[UUID, list[AgentRunStatusEvent]] = {}
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1

    async def save_lead(self, lead: LeadResponse) -> None:
        self._leads[lead.id] = lead

    async def list_leads(self) -> list[LeadResponse]:
        return sorted(
            self._leads.values(),
            key=lambda lead: (
                {"A": 0, "B": 1, "C": 2}[lead.score.tier],
                -lead.score.total,
            ),
        )

    async def get_lead(self, lead_id: UUID) -> LeadResponse | None:
        return self._leads.get(lead_id)

    async def create_queued_agent_run(
        self,
        *,
        run: AgentRunResponse,
        lead: LeadCreate,
        task_id: UUID,
    ) -> None:
        self._runs[run.run_id] = run
        self._run_inputs[run.run_id] = lead
        await self.append_status_event(
            run_id=run.run_id,
            status=run.status,
            current_stage=run.current_stage,
            message="lead received and queued",
        )

    async def save_agent_run(self, run: AgentRunResponse) -> None:
        self._runs[run.run_id] = run
        await self.append_status_event(
            run_id=run.run_id,
            status=run.status,
            current_stage=run.current_stage,
        )

    async def list_agent_runs(self) -> list[AgentRunResponse]:
        return list(self._runs.values())

    async def get_agent_run(self, run_id: UUID) -> AgentRunResponse | None:
        return self._runs.get(run_id)

    async def get_agent_run_input(self, run_id: UUID) -> LeadCreate | None:
        return self._run_inputs.get(run_id)

    async def append_status_event(
        self,
        *,
        run_id: UUID,
        status: str,
        current_stage: str,
        message: str | None = None,
        payload: dict[str, object] | None = None,
    ) -> None:
        self._events.setdefault(run_id, []).append(
            AgentRunStatusEvent(
                id=uuid4(),
                run_id=run_id,
                status=status,
                current_stage=current_stage,
                message=message,
                payload=payload,
            )
        )

    async def list_status_events(self, run_id: UUID) -> list[AgentRunStatusEvent]:
        return self._events.get(run_id, [])

    async def analytics_summary(self) -> AnalyticsSummaryResponse:
        leads = await self.list_leads()
        runs = await self.list_agent_runs()
        tier_distribution = {"A": 0, "B": 0, "C": 0}
        for lead in leads:
            tier_distribution[lead.score.tier] += 1
        market_counts = Counter(lead.enrichment.market for lead in leads)
        total_score = sum(lead.score.total for lead in leads)
        return AnalyticsSummaryResponse(
            total_leads=len(leads),
            tier_distribution=tier_distribution,
            awaiting_review_count=sum(
                1 for run in runs if run.status == "awaiting_review"
            ),
            gate_failed_count=sum(
                1 for lead in leads if lead.gates.status == "failed"
            ),
            average_score=round(total_score / len(leads), 1) if leads else 0.0,
            top_markets=[
                MarketSummary(market=market, lead_count=count)
                for market, count in market_counts.most_common(5)
            ],
        )
