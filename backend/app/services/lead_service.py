from collections import Counter
from collections.abc import AsyncIterator
from uuid import uuid4

from fastapi import Depends

from app.agents.executors.signal_pipeline import SignalPipelineExecutor
from app.agents.states.signal_state import SignalState
from app.core.config import Settings, get_settings
from app.infrastructure.db.session import get_sessionmaker
from app.infrastructure.public_data import get_public_data_client
from app.repositories.base import SignalRepository
from app.repositories.postgres import PostgresSignalRepository
from app.schemas.analytics import AnalyticsSummaryResponse, MarketSummary
from app.schemas.lead import LeadCreate, LeadResponse
from app.schemas.run import AgentRunResponse, AgentStep
from app.services.agent_run_builder import build_agent_run_response
from app.services.demo_seed import DemoSeedRecord
from app.services.lead_response_builder import build_lead_response


class RunTransitionError(ValueError):
    """Raised when an agent run transition is not allowed."""


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
        return await self.create_and_enrich_with_ids(
            lead=lead,
            lead_id=lead_id,
            run_id=run_id,
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
        initial_state: SignalState = {
            "lead_id": lead_id,
            "run_id": run_id,
            "lead": lead,
            "activity_log": [f"{trigger}: lead received"],
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
            trigger=trigger,
        )
        await self.repository.save_lead(response)
        await self.repository.save_agent_run(run)
        await self.repository.commit()
        return response

    async def seed_demo_records(
        self,
        records: list[DemoSeedRecord],
    ) -> list[LeadResponse]:
        seeded: list[LeadResponse] = []
        for record in records:
            seeded.append(
                await self.create_and_enrich_with_ids(
                    lead=record.lead,
                    lead_id=record.lead_id,
                    run_id=record.run_id,
                    trigger="demo_seed",
                )
            )
        return seeded

    async def list_leads(self) -> list[LeadResponse]:
        return await self.repository.list_leads()

    async def get_lead(self, lead_id: str) -> LeadResponse | None:
        return await self.repository.get_lead(lead_id)

    async def list_agent_runs(self) -> list[AgentRunResponse]:
        return await self.repository.list_agent_runs()

    async def get_agent_run(self, run_id: str) -> AgentRunResponse | None:
        return await self.repository.get_agent_run(run_id)

    async def approve_agent_run(self, run_id: str) -> AgentRunResponse | None:
        run = await self.repository.get_agent_run(run_id)
        if run is None:
            return None
        if run.status != "awaiting_review":
            raise RunTransitionError(
                f"Cannot approve run in {run.status!r} status"
            )
        updated = run.model_copy(
            update={
                "status": "completed",
                "current_stage": "review_approved",
                "steps": _update_human_review_step(run.steps, "done"),
                "activity_log": [
                    *run.activity_log,
                    "human_review: approved without send",
                ],
            },
            deep=True,
        )
        await self.repository.save_agent_run(updated)
        await self.repository.commit()
        return updated

    async def pause_agent_run(self, run_id: str) -> AgentRunResponse | None:
        run = await self.repository.get_agent_run(run_id)
        if run is None:
            return None
        if run.status not in {"queued", "running", "awaiting_review"}:
            raise RunTransitionError(f"Cannot pause run in {run.status!r} status")
        updated = run.model_copy(
            update={
                "status": "paused",
                "current_stage": f"{run.current_stage}_paused",
                "activity_log": [*run.activity_log, "agent_run: paused"],
            },
            deep=True,
        )
        await self.repository.save_agent_run(updated)
        await self.repository.commit()
        return updated

    async def analytics_summary(self) -> AnalyticsSummaryResponse:
        leads = await self.repository.list_leads()
        runs = await self.repository.list_agent_runs()
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


def _update_human_review_step(
    steps: list[AgentStep],
    status: str,
) -> list[AgentStep]:
    return [
        step.model_copy(update={"status": status})
        if step.name == "Human review"
        else step
        for step in steps
    ]


async def get_lead_service(
    settings: Settings = Depends(get_settings),
) -> AsyncIterator[LeadService]:
    session_factory = get_sessionmaker(settings)
    async with session_factory() as session:
        yield LeadService(
            PostgresSignalRepository(session),
            pipeline_executor=SignalPipelineExecutor(
                settings=settings,
                public_data_client=get_public_data_client(settings),
            ),
        )
