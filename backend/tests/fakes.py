from app.infrastructure.public_data.fixtures import demo_enrichment
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

    async def commit(self) -> None:
        return None
