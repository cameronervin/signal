from functools import lru_cache
from uuid import uuid4

from app.agents.graph import run_signal_pipeline
from app.agents.state import SignalState
from app.repositories.memory import InMemorySignalRepository
from app.schemas.lead import DraftState, LeadCreate, LeadResponse, ReviewState
from app.schemas.run import AgentRunResponse, AgentStep


class LeadService:
    def __init__(self, repository: InMemorySignalRepository) -> None:
        self.repository = repository

    async def create_and_enrich(self, lead: LeadCreate) -> LeadResponse:
        lead_id = f"lead_{uuid4().hex[:10]}"
        run_id = f"run_{uuid4().hex[:10]}"
        initial_state: SignalState = {
            "lead_id": lead_id,
            "run_id": run_id,
            "lead": lead,
            "activity_log": ["api_insert: lead received"],
        }
        result = await run_signal_pipeline(initial_state)
        gates = result["gates"]
        draft_block_reason = ", ".join(gates.failures) or None
        draft_eligible = gates.status == "passed"
        response = LeadResponse(
            id=lead_id,
            input=lead,
            gates=gates,
            enrichment=result["enrichment"],
            score=result["score"],
            source_facts=result["enrichment"].sources,
            talking_points=result.get("talking_points", []),
            flags=result.get("flags", []),
            draft_state=DraftState(
                eligible=draft_eligible,
                status="awaiting_review" if draft_eligible else "blocked",
                reason=draft_block_reason,
            ),
            review_state=ReviewState(
                status="awaiting_review" if draft_eligible else "blocked",
                reason=draft_block_reason,
            ),
            draft=result.get("draft"),
            related_context=result.get("related_leads", []),
            run_id=run_id,
        )
        current_stage = "human_review" if draft_eligible else "gate_failed"
        run = AgentRunResponse(
            run_id=run_id,
            lead_id=lead_id,
            status="awaiting_review" if draft_eligible else "completed",
            current_stage=current_stage,
            stage_index=3,
            steps=[
                AgentStep(
                    name="Deterministic enrichment",
                    status="done",
                    summary="Geography, market, company, and domain signals resolved.",
                ),
                AgentStep(
                    name="Agent scoring and drafting",
                    status="skipped" if not draft_eligible else "done",
                    summary=(
                        "Draft suppressed because hard gates failed."
                        if not draft_eligible
                        else "Score, why-line, talking points, and draft prepared."
                    ),
                ),
                AgentStep(
                    name="Knowledge graph",
                    status="done",
                    summary="Related-lead context attached.",
                ),
                AgentStep(
                    name="Human review",
                    status="pending" if draft_eligible else "skipped",
                    summary="Awaiting SDR review before any outreach action.",
                ),
            ],
            activity_log=result.get("activity_log", []),
            degraded_reasons=[*gates.failures, *gates.warnings],
        )
        await self.repository.save_lead(response)
        await self.repository.save_agent_run(run)
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
def get_repository() -> InMemorySignalRepository:
    return InMemorySignalRepository()


def get_lead_service() -> LeadService:
    return LeadService(get_repository())
