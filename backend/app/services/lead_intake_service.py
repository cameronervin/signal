from uuid import uuid4

from app.repositories.signal_snapshot import SignalRepository
from app.schemas.lead import LeadCreate, LeadResponse
from app.services.agent_execution_service import AgentExecutionService


class LeadIntakeService:
    """Use cases for inbound lead intake and lead retrieval."""

    def __init__(
        self,
        repository: SignalRepository,
        *,
        agent_execution_service: AgentExecutionService,
    ) -> None:
        self.repository = repository
        self.agent_execution_service = agent_execution_service

    async def create_and_enrich(self, lead: LeadCreate) -> LeadResponse:
        return await self.create_and_enrich_with_ids(
            lead=lead,
            lead_id=f"lead_{uuid4().hex[:10]}",
            run_id=f"run_{uuid4().hex[:10]}",
            trigger="api_insert",
        )

    async def create_and_enrich_with_ids(
        self,
        *,
        lead: LeadCreate,
        lead_id: str,
        run_id: str,
        trigger: str,
    ) -> LeadResponse:
        return await self.agent_execution_service.execute_for_inbound_lead(
            lead=lead,
            lead_id=lead_id,
            run_id=run_id,
            trigger=trigger,
        )

    async def list_leads(self) -> list[LeadResponse]:
        return await self.repository.list_leads()

    async def get_lead(self, lead_id: str) -> LeadResponse | None:
        return await self.repository.get_lead(lead_id)
