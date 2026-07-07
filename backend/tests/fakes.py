from collections import Counter

from app.infrastructure.public_data.fixtures import demo_enrichment
from app.schemas.analytics import AnalyticsSummaryResponse, MarketSummary
from app.schemas.lead import LeadCreate, LeadResponse
from app.schemas.run import AgentRunResponse


class FakePublicDataClient:
    def __init__(self) -> None:
        self.calls = 0

    async def enrich(self, lead: LeadCreate):
        self.calls += 1
        return demo_enrichment(lead.company, lead.city, lead.state)


class FakeSignalRepository:
    def __init__(self) -> None:
        self._leads: dict[str, LeadResponse] = {}
        self._runs: dict[str, AgentRunResponse] = {}

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

    async def get_lead(self, lead_id: str) -> LeadResponse | None:
        return self._leads.get(lead_id)

    async def save_agent_run(self, run: AgentRunResponse) -> None:
        self._runs[run.run_id] = run

    async def list_agent_runs(self) -> list[AgentRunResponse]:
        return list(self._runs.values())

    async def get_agent_run(self, run_id: str) -> AgentRunResponse | None:
        return self._runs.get(run_id)

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
