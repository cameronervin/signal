from functools import lru_cache
from typing import Literal, Protocol
from uuid import uuid4

from pydantic import BaseModel

from app.agents.fixtures import demo_seed_leads
from app.agents.graph import run_signal_pipeline
from app.agents.state import SignalState
from app.core.config import get_settings
from app.repositories.memory import InMemorySignalRepository
from app.schemas.lead import (
    Enrichment,
    GateResult,
    LeadCreate,
    LeadResponse,
    ScoreBreakdown,
    SeedLeadResult,
    SeedLeadsResponse,
)
from app.schemas.run import AgentRunResponse, AgentStep, ExecutionMode


class WorkerDispatch(BaseModel):
    task_id: str
    queue: str


class AgentRunDispatcher(Protocol):
    async def dispatch_agent_run(
        self,
        *,
        lead_id: str,
        run_id: str,
    ) -> WorkerDispatch: ...


class LeadService:
    def __init__(
        self,
        repository: InMemorySignalRepository,
        *,
        execution_mode: ExecutionMode = "inline",
        worker_dispatcher: AgentRunDispatcher | None = None,
        worker_queue: str = "signal-agent-runs",
    ) -> None:
        self.repository = repository
        self.execution_mode = execution_mode
        self.worker_dispatcher = worker_dispatcher
        self.worker_queue = worker_queue

    async def create_and_enrich(self, lead: LeadCreate) -> LeadResponse:
        lead_id = f"lead_{uuid4().hex[:10]}"
        run_id = f"run_{uuid4().hex[:10]}"
        return await self._create_and_enrich_with_ids(
            lead,
            lead_id=lead_id,
            run_id=run_id,
            trigger="api_insert",
            execution_mode=self.execution_mode,
        )

    async def seed_demo_leads(self, *, reset: bool = True) -> SeedLeadsResponse:
        if reset:
            await self.repository.reset()

        results: list[SeedLeadResult] = []
        for seed in demo_seed_leads():
            lead = await self._create_and_enrich_with_ids(
                seed.input,
                lead_id=seed.lead_id,
                run_id=seed.run_id,
                trigger="demo_seed",
                execution_mode="inline",
            )
            results.append(
                SeedLeadResult(
                    handle=seed.handle,
                    lead_id=lead.id,
                    run_id=lead.run_id,
                    tier=lead.score.tier,
                    gate_status=lead.gates.status,
                    draft_available=lead.draft is not None,
                )
            )

        return SeedLeadsResponse(reset=reset, count=len(results), seeds=results)

    async def _create_and_enrich_with_ids(
        self,
        lead: LeadCreate,
        *,
        lead_id: str,
        run_id: str,
        trigger: Literal["api_insert", "demo_seed"],
        execution_mode: ExecutionMode,
    ) -> LeadResponse:
        if execution_mode == "worker" and self.worker_dispatcher is not None:
            return await self._queue_worker_run(
                lead,
                lead_id=lead_id,
                run_id=run_id,
                trigger=trigger,
            )

        dispatch = await self._dispatch_worker_run(
            lead_id=lead_id,
            run_id=run_id,
            execution_mode=execution_mode,
        )
        initial_state: SignalState = {
            "lead_id": lead_id,
            "run_id": run_id,
            "trigger": trigger,
            "lead": lead,
            "activity_log": [f"{trigger}: lead received"],
        }
        result = await run_signal_pipeline(initial_state)
        response = LeadResponse(
            id=lead_id,
            input=lead,
            gates=result["gates"],
            enrichment=result["enrichment"],
            score=result["score"],
            talking_points=result.get("talking_points", []),
            flags=result.get("flags", []),
            draft=result.get("draft"),
            related_leads=result.get("related_leads", []),
            run_id=run_id,
        )
        run = self._build_run_response(
            response=response,
            run_id=run_id,
            lead_id=lead_id,
            trigger=trigger,
            execution_mode=execution_mode,
            dispatch=dispatch,
            activity_log=result.get("activity_log", []),
            degraded_reasons=result.get("degraded_reasons", []),
        )
        response = response.model_copy(update={"run": run})
        await self.repository.save_lead(response)
        await self.repository.save_agent_run(run)
        return response

    async def _queue_worker_run(
        self,
        lead: LeadCreate,
        *,
        lead_id: str,
        run_id: str,
        trigger: Literal["api_insert", "demo_seed"],
    ) -> LeadResponse:
        response = self._build_queued_lead_response(
            lead=lead,
            lead_id=lead_id,
            run_id=run_id,
            trigger=trigger,
        )
        await self.repository.save_lead(response)
        await self.repository.save_agent_run(response.run)

        dispatch = await self._dispatch_worker_run(
            lead_id=lead_id,
            run_id=run_id,
            execution_mode="worker",
        )
        if dispatch is None:
            return response

        run = response.run.model_copy(
            update={
                "task_id": dispatch.task_id,
                "worker_queue": dispatch.queue,
                "activity_log": [
                    *response.run.activity_log,
                    "worker_dispatch: queued",
                ],
            }
        )
        response = response.model_copy(update={"run": run})
        await self.repository.save_lead(response)
        await self.repository.save_agent_run(run)
        return response

    def _build_queued_lead_response(
        self,
        *,
        lead: LeadCreate,
        lead_id: str,
        run_id: str,
        trigger: Literal["api_insert", "demo_seed"],
    ) -> LeadResponse:
        run = AgentRunResponse(
            run_id=run_id,
            lead_id=lead_id,
            status="queued",
            trigger=trigger,
            execution_mode="worker",
            current_stage="queued",
            steps=[
                AgentStep(
                    stage="deterministic_enrichment",
                    name="Deterministic enrichment",
                    status="pending",
                    summary="Waiting for worker execution.",
                ),
                AgentStep(
                    stage="agent_scoring_and_drafting",
                    name="Agent scoring and drafting",
                    status="pending",
                    summary="Waiting for worker execution.",
                ),
                AgentStep(
                    stage="knowledge_graph",
                    name="Knowledge graph",
                    status="pending",
                    summary="Waiting for worker execution.",
                ),
                AgentStep(
                    stage="human_review",
                    name="Human review",
                    status="pending",
                    summary="Awaiting agent output before SDR review.",
                ),
            ],
            activity_log=[f"{trigger}: lead received"],
        )
        return LeadResponse(
            id=lead_id,
            input=lead,
            gates=GateResult(status="pending"),
            enrichment=Enrichment(market=f"{lead.city}, {lead.state}"),
            score=ScoreBreakdown(
                total=0,
                tier="C",
                company_fit=0,
                market_opportunity=0,
                why_line="Agent run queued; score pending.",
            ),
            talking_points=[],
            flags=[],
            draft=None,
            related_leads=[],
            run_id=run_id,
            run=run,
        )

    async def _dispatch_worker_run(
        self,
        *,
        lead_id: str,
        run_id: str,
        execution_mode: ExecutionMode,
    ) -> WorkerDispatch | None:
        if execution_mode != "worker":
            return None
        if self.worker_dispatcher is None:
            return WorkerDispatch(
                task_id=f"worker_fallback_{run_id}",
                queue=self.worker_queue,
            )
        return await self.worker_dispatcher.dispatch_agent_run(
            lead_id=lead_id,
            run_id=run_id,
        )

    def _build_run_response(
        self,
        *,
        response: LeadResponse,
        run_id: str,
        lead_id: str,
        trigger: str,
        execution_mode: ExecutionMode,
        dispatch: WorkerDispatch | None,
        activity_log: list[str],
        degraded_reasons: list[str],
    ) -> AgentRunResponse:
        degraded_reasons = [*degraded_reasons]
        if response.gates.status == "failed":
            degraded_reasons.append("draft_suppressed: hard gate failed")
        if execution_mode == "worker" and self.worker_dispatcher is None:
            degraded_reasons.append("worker_dispatch_unavailable: eager fallback")

        return AgentRunResponse(
            run_id=run_id,
            lead_id=lead_id,
            status=(
                "awaiting_review"
                if response.gates.status == "passed"
                else "completed"
            ),
            trigger=trigger,
            execution_mode=execution_mode,
            task_id=dispatch.task_id if dispatch is not None else None,
            worker_queue=dispatch.queue if dispatch is not None else None,
            current_stage=(
                "human_review" if response.gates.status == "passed" else "gate_failed"
            ),
            steps=[
                AgentStep(
                    stage="deterministic_enrichment",
                    name="Deterministic enrichment",
                    status="done",
                    summary="Geography, market, company, and domain signals resolved.",
                ),
                AgentStep(
                    stage="agent_scoring_and_drafting",
                    name="Agent scoring and drafting",
                    status="skipped" if response.gates.status == "failed" else "done",
                    summary=(
                        "Draft suppressed because hard gates failed."
                        if response.gates.status == "failed"
                        else "Score, why-line, talking points, and draft prepared."
                    ),
                ),
                AgentStep(
                    stage="knowledge_graph",
                    name="Knowledge graph",
                    status="done",
                    summary="Related-lead context attached.",
                ),
                AgentStep(
                    stage="human_review",
                    name="Human review",
                    status=(
                        "pending" if response.gates.status == "passed" else "skipped"
                    ),
                    summary="Awaiting SDR review before any outreach action.",
                ),
            ],
            activity_log=activity_log,
            degraded_reasons=degraded_reasons,
        )

    async def list_leads(self) -> list[LeadResponse]:
        return await self.repository.list_leads()

    async def get_lead(self, lead_id: str) -> LeadResponse | None:
        return await self.repository.get_lead(lead_id)

    async def list_agent_runs(self) -> list[AgentRunResponse]:
        return await self.repository.list_agent_runs()

    async def get_agent_run(self, run_id: str) -> AgentRunResponse | None:
        return await self.repository.get_agent_run(run_id)


@lru_cache
def get_repository() -> InMemorySignalRepository:
    return InMemorySignalRepository()


async def get_lead_service() -> LeadService:
    settings = get_settings()
    return LeadService(
        get_repository(),
        execution_mode=settings.agent_execution_mode,
        worker_queue=settings.celery_agent_queue,
    )
