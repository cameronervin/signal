from collections.abc import AsyncIterator
from functools import lru_cache
from uuid import uuid4

from fastapi import Depends

from app.agents.executors.signal_pipeline import SignalPipelineExecutor
from app.agents.states.signal_state import SignalState
from app.core.config import Settings, get_settings
from app.infrastructure.db.session import get_sessionmaker
from app.infrastructure.public_data import get_public_data_client
from app.repositories.base import SignalRepository
from app.repositories.memory import InMemorySignalRepository
from app.repositories.postgres import PostgresSignalRepository
from app.schemas.lead import LeadCreate, LeadResponse
from app.schemas.run import AgentRunResponse
from app.services.agent_run_builder import build_agent_run_response
from app.services.lead_response_builder import build_lead_response


class LeadService:
    def __init__(
        self,
        repository: SignalRepository,
        *,
        pipeline_executor: SignalPipelineExecutor | None = None,
    ) -> None:
        self.repository = repository
        self.pipeline_executor = pipeline_executor or SignalPipelineExecutor()

    async def create_and_enrich(self, lead: LeadCreate) -> LeadResponse:
        lead_id = f"lead_{uuid4().hex[:10]}"
        run_id = f"run_{uuid4().hex[:10]}"
        initial_state: SignalState = {
            "lead_id": lead_id,
            "run_id": run_id,
            "lead": lead,
            "activity_log": ["api_insert: lead received"],
        }
        result = await self.pipeline_executor.execute(initial_state)
        response = build_lead_response(
            lead_id=lead_id,
            run_id=run_id,
            lead=lead,
            result=result,
        )
        run = build_agent_run_response(
            lead=response,
            activity_log=result.get("activity_log", []),
        )
        await self.repository.save_lead(response)
        await self.repository.save_agent_run(run)
        await self.repository.commit()
        return response

    async def list_leads(self) -> list[LeadResponse]:
        return await self.repository.list_leads()

    async def get_lead(self, lead_id: str) -> LeadResponse | None:
        return await self.repository.get_lead(lead_id)

    async def list_agent_runs(self) -> list[AgentRunResponse]:
        return await self.repository.list_agent_runs()

    async def get_agent_run(self, run_id: str) -> AgentRunResponse | None:
        return await self.repository.get_agent_run(run_id)


@lru_cache
def get_memory_repository() -> InMemorySignalRepository:
    return InMemorySignalRepository()


async def get_lead_service(
    settings: Settings = Depends(get_settings),
) -> AsyncIterator[LeadService]:
    if settings.repository_backend == "memory":
        yield LeadService(
            get_memory_repository(),
            pipeline_executor=SignalPipelineExecutor(
                settings=settings,
                public_data_client=get_public_data_client(settings),
            ),
        )
        return

    session_factory = get_sessionmaker(settings)
    async with session_factory() as session:
        yield LeadService(
            PostgresSignalRepository(session),
            pipeline_executor=SignalPipelineExecutor(
                settings=settings,
                public_data_client=get_public_data_client(settings),
            ),
        )
