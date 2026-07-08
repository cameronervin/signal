from collections import Counter
from datetime import datetime
from uuid import UUID, uuid4

from app.agents.context.digital_worker_lifecycle import DigitalWorkerLifecycleSpec
from app.infrastructure.public_data.fixtures import demo_enrichment
from app.schemas.analytics import AnalyticsSummaryResponse, MarketSummary
from app.schemas.digital_worker import (
    DigitalWorkerAssignmentResponse,
    DigitalWorkerFollowUpResponse,
    DigitalWorkerGoalStateResponse,
    DigitalWorkerMessageResponse,
    DigitalWorkerRunResponse,
    DigitalWorkerTrigger,
)
from app.schemas.lead import (
    LeadCreate,
    LeadDeleteResponse,
    LeadQueueItemResponse,
    LeadResponse,
)
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
        self.active_assignment_lead_ids: set[UUID] = set()
        self.worker_cleanup_counts_by_lead: dict[UUID, dict[str, int]] = {}
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

    async def list_lead_queue_items(self) -> list[LeadQueueItemResponse]:
        ready_leads = await self.list_leads()
        items = [
            LeadQueueItemResponse(
                id=lead.id,
                run_id=lead.run_id,
                state="ready",
                input=lead.input,
                lead=lead,
            )
            for lead in ready_leads
        ]
        ready_lead_ids = {lead.id for lead in ready_leads}

        for run in reversed(list(self._runs.values())):
            if (
                run.status not in {"queued", "running"}
                or run.lead_id in ready_lead_ids
                or run.run_id not in self._run_inputs
            ):
                continue
            items.append(
                LeadQueueItemResponse(
                    id=run.lead_id,
                    run_id=run.run_id,
                    state="loading",
                    input=self._run_inputs[run.run_id],
                    run=run,
                )
            )
        return items

    async def get_lead(self, lead_id: UUID) -> LeadResponse | None:
        return self._leads.get(lead_id)

    async def delete_lead_intelligence(
        self,
        lead_id: UUID,
        *,
        include_digital_worker: bool = False,
    ) -> LeadDeleteResponse:
        if lead_id in self.active_assignment_lead_ids and not include_digital_worker:
            return LeadDeleteResponse(
                deleted_leads=0,
                deleted_agent_runs=0,
                deleted_status_events=0,
                skipped_assigned_leads=1,
            )

        run_ids = [
            run_id for run_id, run in self._runs.items() if run.lead_id == lead_id
        ]
        deleted_status_events = sum(
            len(self._events.get(run_id, [])) for run_id in run_ids
        )
        deleted_leads = 1 if lead_id in self._leads else 0
        deleted_agent_runs = len(run_ids)

        self._leads.pop(lead_id, None)
        for run_id in run_ids:
            self._runs.pop(run_id, None)
            self._run_inputs.pop(run_id, None)
            self._events.pop(run_id, None)
        worker_counts = {}
        if include_digital_worker:
            worker_counts = self.worker_cleanup_counts_by_lead.pop(lead_id, {})
            self.active_assignment_lead_ids.discard(lead_id)

        return LeadDeleteResponse(
            deleted_leads=deleted_leads,
            deleted_agent_runs=deleted_agent_runs,
            deleted_status_events=deleted_status_events,
            skipped_assigned_leads=0,
            deleted_worker_assignments=worker_counts.get("assignments", 0),
            deleted_worker_runs=worker_counts.get("runs", 0),
            deleted_worker_goal_states=worker_counts.get("goal_states", 0),
            deleted_worker_messages=worker_counts.get("messages", 0),
            deleted_worker_follow_ups=worker_counts.get("follow_ups", 0),
        )

    async def delete_all_lead_intelligence(self) -> LeadDeleteResponse:
        candidate_lead_ids = {
            *self._leads.keys(),
            *(run.lead_id for run in self._runs.values()),
        }
        blocked_lead_ids = candidate_lead_ids & self.active_assignment_lead_ids
        deletable_lead_ids = candidate_lead_ids - blocked_lead_ids
        run_ids = [
            run_id
            for run_id, run in self._runs.items()
            if run.lead_id in deletable_lead_ids
        ]
        deleted_status_events = sum(
            len(self._events.get(run_id, [])) for run_id in run_ids
        )
        deleted_leads = sum(
            1 for lead_id in deletable_lead_ids if lead_id in self._leads
        )
        deleted_agent_runs = len(run_ids)

        for lead_id in deletable_lead_ids:
            self._leads.pop(lead_id, None)
        for run_id in run_ids:
            self._runs.pop(run_id, None)
            self._run_inputs.pop(run_id, None)
            self._events.pop(run_id, None)

        return LeadDeleteResponse(
            deleted_leads=deleted_leads,
            deleted_agent_runs=deleted_agent_runs,
            deleted_status_events=deleted_status_events,
            skipped_assigned_leads=len(blocked_lead_ids),
        )

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


class FakeDigitalWorkerRepository:
    def __init__(self) -> None:
        self._assignments: dict[UUID, dict[str, object]] = {}
        self._goals: dict[UUID, list[DigitalWorkerGoalStateResponse]] = {}
        self._messages: dict[UUID, list[DigitalWorkerMessageResponse]] = {}
        self._follow_ups: dict[UUID, list[DigitalWorkerFollowUpResponse]] = {}
        self._runs: dict[UUID, DigitalWorkerRunResponse] = {}
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1

    async def create_assignment(
        self,
        *,
        lead_id: UUID,
        lifecycle: DigitalWorkerLifecycleSpec,
    ) -> DigitalWorkerAssignmentResponse:
        assignment_id = uuid4()
        self._assignments[assignment_id] = {
            "assignment_id": assignment_id,
            "lead_id": lead_id,
            "status": "active",
            "current_phase": lifecycle.initial_phase,
            "lifecycle_version": lifecycle.version,
            "latest_run_id": None,
            "activity_log": [
                "assignment: SDR assigned digital worker",
                "worker: lifecycle goals initialized",
            ],
        }
        self._goals[assignment_id] = [
            DigitalWorkerGoalStateResponse(
                phase_key=phase.key,
                goal_key=goal.key,
                status="pending",
            )
            for phase in lifecycle.phases
            for goal in phase.goals
        ]
        self._messages[assignment_id] = []
        self._follow_ups[assignment_id] = []
        return await self.get_assignment_required(assignment_id)

    async def list_assignments(self) -> list[DigitalWorkerAssignmentResponse]:
        return [
            await self.get_assignment_required(assignment_id)
            for assignment_id in self._assignments
        ]

    async def get_assignment(
        self,
        assignment_id: UUID,
    ) -> DigitalWorkerAssignmentResponse | None:
        if assignment_id not in self._assignments:
            return None
        return await self.get_assignment_required(assignment_id)

    async def get_assignment_required(
        self,
        assignment_id: UUID,
    ) -> DigitalWorkerAssignmentResponse:
        data = self._assignments[assignment_id]
        runs = [
            run for run in self._runs.values() if run.assignment_id == assignment_id
        ]
        return DigitalWorkerAssignmentResponse(
            assignment_id=assignment_id,
            lead_id=data["lead_id"],
            status=data["status"],
            current_phase=data["current_phase"],
            lifecycle_version=data["lifecycle_version"],
            latest_run_id=data["latest_run_id"],
            activity_log=list(data["activity_log"]),
            goals=list(self._goals.get(assignment_id, [])),
            messages=list(self._messages.get(assignment_id, [])),
            follow_ups=list(self._follow_ups.get(assignment_id, [])),
            runs=runs,
        )

    async def get_active_assignment_for_lead(
        self,
        lead_id: UUID,
    ) -> DigitalWorkerAssignmentResponse | None:
        for assignment_id, data in self._assignments.items():
            if data["lead_id"] == lead_id and data["status"] in {"active", "paused"}:
                return await self.get_assignment_required(assignment_id)
        return None

    async def create_run(
        self,
        *,
        assignment_id: UUID,
        trigger: DigitalWorkerTrigger,
    ) -> DigitalWorkerRunResponse:
        data = self._assignments[assignment_id]
        run = DigitalWorkerRunResponse(
            run_id=uuid4(),
            assignment_id=assignment_id,
            trigger=trigger,
            status="queued",
            current_phase=data["current_phase"],
            message="digital worker queued",
        )
        self._runs[run.run_id] = run
        data["latest_run_id"] = run.run_id
        data["activity_log"].append(f"{trigger}: worker queued")
        return run

    async def get_run(self, run_id: UUID) -> DigitalWorkerRunResponse | None:
        return self._runs.get(run_id)

    async def update_run_status(
        self,
        *,
        run_id: UUID,
        status: str,
        message: str | None = None,
    ) -> DigitalWorkerRunResponse | None:
        run = self._runs.get(run_id)
        if run is None:
            return None
        assignment = self._assignments[run.assignment_id]
        updated = run.model_copy(
            update={
                "status": status,
                "message": message or run.message,
                "current_phase": assignment["current_phase"],
            }
        )
        self._runs[run_id] = updated
        assignment["activity_log"].append(f"worker_run: {status}")
        return updated

    async def add_message(
        self,
        *,
        assignment_id: UUID,
        direction: str,
        subject: str,
        body: str,
        external_message_id: str | None = None,
    ) -> DigitalWorkerMessageResponse:
        message = DigitalWorkerMessageResponse(
            message_id=uuid4(),
            assignment_id=assignment_id,
            direction=direction,
            subject=subject,
            body=body,
            external_message_id=external_message_id,
        )
        self._messages.setdefault(assignment_id, []).append(message)
        self._assignments[assignment_id]["activity_log"].append(
            f"email: {direction} sandbox message"
        )
        return message

    async def complete_goal(
        self,
        *,
        assignment_id: UUID,
        phase_key: str,
        goal_key: str,
        notes: str | None = None,
    ) -> None:
        goals = self._goals.get(assignment_id, [])
        self._goals[assignment_id] = [
            goal.model_copy(update={"status": "completed", "notes": notes})
            if goal.phase_key == phase_key and goal.goal_key == goal_key
            else goal
            for goal in goals
        ]
        self._assignments[assignment_id]["activity_log"].append(
            f"goal: {goal_key} completed"
        )

    async def update_assignment_state(
        self,
        *,
        assignment_id: UUID,
        status: str | None = None,
        current_phase: str | None = None,
        activity: str | None = None,
    ) -> DigitalWorkerAssignmentResponse | None:
        data = self._assignments.get(assignment_id)
        if data is None:
            return None
        if status is not None:
            data["status"] = status
        if current_phase is not None:
            data["current_phase"] = current_phase
        if activity is not None:
            data["activity_log"].append(activity)
        return await self.get_assignment_required(assignment_id)

    async def schedule_follow_up(
        self,
        *,
        assignment_id: UUID,
        due_at: datetime,
        reason: str,
    ) -> DigitalWorkerFollowUpResponse:
        follow_up = DigitalWorkerFollowUpResponse(
            follow_up_id=uuid4(),
            assignment_id=assignment_id,
            status="pending",
            due_at=due_at,
            reason=reason,
        )
        self._follow_ups.setdefault(assignment_id, []).append(follow_up)
        self._assignments[assignment_id]["activity_log"].append(
            "follow_up: scheduled"
        )
        return follow_up

    async def complete_claimed_follow_ups(self, *, run_id: UUID) -> None:
        for assignment_id, follow_ups in self._follow_ups.items():
            self._follow_ups[assignment_id] = [
                follow_up.model_copy(update={"status": "completed"})
                if follow_up.claimed_run_id == run_id
                else follow_up
                for follow_up in follow_ups
            ]

    async def claim_due_follow_ups(
        self,
        *,
        now: datetime,
        limit: int,
    ) -> list[DigitalWorkerRunResponse]:
        runs: list[DigitalWorkerRunResponse] = []
        for assignment_id, follow_ups in self._follow_ups.items():
            data = self._assignments[assignment_id]
            if data["status"] != "active":
                continue
            updated_follow_ups: list[DigitalWorkerFollowUpResponse] = []
            for follow_up in follow_ups:
                if (
                    len(runs) < limit
                    and follow_up.status == "pending"
                    and follow_up.due_at <= now
                ):
                    run = await self.create_run(
                        assignment_id=assignment_id,
                        trigger="follow_up_due",
                    )
                    follow_up = follow_up.model_copy(
                        update={"status": "claimed", "claimed_run_id": run.run_id}
                    )
                    runs.append(run)
                updated_follow_ups.append(follow_up)
            self._follow_ups[assignment_id] = updated_follow_ups
        return runs
