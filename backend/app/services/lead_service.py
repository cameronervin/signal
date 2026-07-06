from uuid import uuid4

from app.agents.graph import run_signal_pipeline
from app.agents.state import SignalState
from app.repositories.memory import InMemorySignalRepository
from app.schemas.lead import LeadCreate, LeadResponse
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
        run = AgentRunResponse(
            run_id=run_id,
            lead_id=lead_id,
            status=(
                "awaiting_review"
                if response.gates.status == "passed"
                else "completed"
            ),
            current_stage=(
                "human_review" if response.gates.status == "passed" else "gate_failed"
            ),
            steps=[
                AgentStep(
                    name="Deterministic enrichment",
                    status="done",
                    summary="Geography, market, company, and domain signals resolved.",
                ),
                AgentStep(
                    name="Agent scoring and drafting",
                    status="skipped" if response.gates.status == "failed" else "done",
                    summary=(
                        "Draft suppressed because hard gates failed."
                        if response.gates.status == "failed"
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
                    status=(
                        "pending" if response.gates.status == "passed" else "skipped"
                    ),
                    summary="Awaiting SDR review before any outreach action.",
                ),
            ],
            activity_log=result.get("activity_log", []),
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
