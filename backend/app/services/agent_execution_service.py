from app.agents.executors.signal_pipeline import SignalPipelineExecutor
from app.agents.states.signal_state import SignalState
from app.repositories.signal_snapshot import SignalRepository
from app.schemas.knowledge_graph import LeadKnowledgeGraph
from app.schemas.lead import LeadCreate, LeadResponse
from app.schemas.run import AgentRunResponse, AgentStep


class AgentExecutionService:
    """Execute Signal's inbound lead intelligence workflow."""

    def __init__(
        self,
        repository: SignalRepository,
        *,
        pipeline_executor: SignalPipelineExecutor | None = None,
    ) -> None:
        self.repository = repository
        self.pipeline_executor = pipeline_executor

    async def execute_for_inbound_lead(
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
        try:
            executor = self.pipeline_executor or SignalPipelineExecutor()
            result = await executor.execute(initial_state)
        except Exception:
            await self.repository.save_agent_run(
                self._build_failed_run_response(
                    lead_id=lead_id,
                    run_id=run_id,
                    trigger=trigger,
                    activity_log=[
                        *initial_state["activity_log"],
                        "agent_execution: failed",
                    ],
                )
            )
            raise

        response = self._build_lead_response(
            lead_id=lead_id,
            run_id=run_id,
            lead=lead,
            result=result,
        )
        run = self._build_agent_run_response(
            lead=response,
            activity_log=result.get("activity_log", []),
            trigger=trigger,
        )
        await self.repository.save_lead(response)
        await self.repository.save_agent_run(run)
        return response

    def _build_lead_response(
        self,
        *,
        lead_id: str,
        run_id: str,
        lead: LeadCreate,
        result: SignalState,
    ) -> LeadResponse:
        return LeadResponse(
            id=lead_id,
            input=lead,
            gates=result["gates"],
            enrichment=result["enrichment"],
            score=result["score"],
            talking_points=result.get("talking_points", []),
            flags=result.get("flags", []),
            draft=result.get("draft"),
            related_leads=result.get("related_leads", []),
            knowledge_graph=result.get("knowledge_graph", LeadKnowledgeGraph()),
            run_id=run_id,
        )

    def _build_agent_run_response(
        self,
        *,
        lead: LeadResponse,
        activity_log: list[str],
        trigger: str = "api_insert",
    ) -> AgentRunResponse:
        gates_passed = lead.gates.status == "passed"
        model_drafting_failed = gates_passed and lead.draft is None
        return AgentRunResponse(
            run_id=lead.run_id,
            lead_id=lead.id,
            status=(
                "failed"
                if model_drafting_failed
                else "awaiting_review"
                if gates_passed
                else "completed"
            ),
            trigger=trigger,
            current_stage=(
                "model_drafting_failed"
                if model_drafting_failed
                else "human_review"
                if gates_passed
                else "gate_failed"
            ),
            steps=[
                AgentStep(
                    name="Deterministic enrichment",
                    status="done",
                    summary="Geography, market, company, and domain signals resolved.",
                ),
                AgentStep(
                    name="Deterministic scoring",
                    status="done",
                    summary="Score, tier, why-line, and talking points computed.",
                ),
                AgentStep(
                    name="Agent research and drafting",
                    status=(
                        "failed"
                        if model_drafting_failed
                        else "done"
                        if gates_passed
                        else "skipped"
                    ),
                    summary=(
                        "Optional research completed and draft prepared."
                        if gates_passed
                        and not model_drafting_failed
                        else "Model drafting failed; no draft was produced."
                        if model_drafting_failed
                        else "Draft suppressed because hard gates failed."
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
                        "pending"
                        if gates_passed and not model_drafting_failed
                        else "skipped"
                    ),
                    summary=(
                        "Awaiting SDR review before any outreach action."
                        if gates_passed
                        and not model_drafting_failed
                        else "Review skipped because no draft was produced."
                        if model_drafting_failed
                        else "Review skipped because hard gates failed."
                    ),
                ),
            ],
            activity_log=activity_log,
        )

    def _build_failed_run_response(
        self,
        *,
        lead_id: str,
        run_id: str,
        trigger: str,
        activity_log: list[str],
    ) -> AgentRunResponse:
        return AgentRunResponse(
            run_id=run_id,
            lead_id=lead_id,
            status="failed",
            trigger=trigger,
            current_stage="agent_execution_failed",
            steps=[
                AgentStep(
                    name="Agent execution",
                    status="failed",
                    summary=(
                        "Pipeline execution failed before a lead snapshot was "
                        "produced."
                    ),
                )
            ],
            activity_log=activity_log,
        )
