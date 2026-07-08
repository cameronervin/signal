from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from app.infrastructure.public_data.fixtures import demo_enrichment
from app.schemas.digital_worker import DigitalWorkerAssignmentCreate
from app.schemas.knowledge_graph import LeadKnowledgeGraph
from app.schemas.lead import (
    DraftEmail,
    GateResult,
    LeadCreate,
    LeadResponse,
    ScoreBreakdown,
)
from app.services.digital_worker_service import (
    DigitalWorkerEligibilityError,
    DigitalWorkerService,
    DigitalWorkerTransitionError,
)
from tests.fakes import FakeDigitalWorkerRepository, FakeSignalRepository


@pytest.mark.asyncio
async def test_assignment_execute_sends_existing_draft_and_schedules_follow_up():
    signal_repository = FakeSignalRepository()
    worker_repository = FakeDigitalWorkerRepository()
    lead = _lead_response()
    await signal_repository.save_lead(lead)
    service = DigitalWorkerService(
        signal_repository=signal_repository,
        worker_repository=worker_repository,
        task_dispatcher=CollectingDispatcher(),
    )

    assignment = await service.assign_lead(
        DigitalWorkerAssignmentCreate(lead_id=lead.id)
    )
    run_id = assignment.latest_run_id
    assert run_id is not None

    await service.execute_run(run_id)
    updated = await service.get_assignment(assignment.assignment_id)

    assert updated.current_phase == "reply_qualification"
    assert updated.messages[0].direction == "outbound"
    assert updated.messages[0].subject == lead.draft.subject
    assert updated.follow_ups[0].status == "pending"
    completed_goals = {
        goal.goal_key for goal in updated.goals if goal.status == "completed"
    }
    assert {"send_existing_draft", "schedule_first_follow_up"} <= completed_goals


@pytest.mark.asyncio
async def test_assignment_rejects_gate_failed_lead():
    signal_repository = FakeSignalRepository()
    worker_repository = FakeDigitalWorkerRepository()
    lead = _lead_response(gate_status="failed", draft=None)
    await signal_repository.save_lead(lead)
    service = DigitalWorkerService(
        signal_repository=signal_repository,
        worker_repository=worker_repository,
        task_dispatcher=CollectingDispatcher(),
    )

    with pytest.raises(DigitalWorkerEligibilityError):
        await service.assign_lead(DigitalWorkerAssignmentCreate(lead_id=lead.id))


@pytest.mark.asyncio
async def test_duplicate_active_assignment_is_rejected():
    signal_repository = FakeSignalRepository()
    worker_repository = FakeDigitalWorkerRepository()
    lead = _lead_response()
    await signal_repository.save_lead(lead)
    service = DigitalWorkerService(
        signal_repository=signal_repository,
        worker_repository=worker_repository,
        task_dispatcher=CollectingDispatcher(),
    )

    await service.assign_lead(DigitalWorkerAssignmentCreate(lead_id=lead.id))

    with pytest.raises(DigitalWorkerTransitionError):
        await service.assign_lead(DigitalWorkerAssignmentCreate(lead_id=lead.id))


@pytest.mark.asyncio
async def test_inbound_email_wakes_worker_and_marks_meeting_ready():
    signal_repository = FakeSignalRepository()
    worker_repository = FakeDigitalWorkerRepository()
    lead = _lead_response()
    await signal_repository.save_lead(lead)
    dispatcher = CollectingDispatcher()
    service = DigitalWorkerService(
        signal_repository=signal_repository,
        worker_repository=worker_repository,
        task_dispatcher=dispatcher,
    )
    assignment = await service.assign_lead(
        DigitalWorkerAssignmentCreate(lead_id=lead.id)
    )

    from app.schemas.digital_worker import DigitalWorkerInboundEmailCreate

    await service.record_inbound_email(
        assignment_id=assignment.assignment_id,
        payload=DigitalWorkerInboundEmailCreate(
            subject="Re: leasing follow-up",
            body="Can we schedule a call next week?",
        ),
    )
    await service.execute_run(dispatcher.run_ids[-1])
    updated = await service.get_assignment(assignment.assignment_id)

    assert updated.status == "completed"
    assert updated.current_phase == "meeting_handoff"
    assert any("meeting-ready" in item for item in updated.activity_log)


@pytest.mark.asyncio
async def test_due_follow_up_claiming_queues_runs_for_active_assignments():
    signal_repository = FakeSignalRepository()
    worker_repository = FakeDigitalWorkerRepository()
    lead = _lead_response()
    await signal_repository.save_lead(lead)
    service = DigitalWorkerService(
        signal_repository=signal_repository,
        worker_repository=worker_repository,
        task_dispatcher=CollectingDispatcher(),
    )
    assignment = await service.assign_lead(
        DigitalWorkerAssignmentCreate(lead_id=lead.id)
    )
    await worker_repository.schedule_follow_up(
        assignment_id=assignment.assignment_id,
        due_at=datetime.now(UTC) - timedelta(minutes=1),
        reason="test due",
    )

    runs = await service.claim_due_follow_ups(limit=10)

    assert len(runs) == 1
    assert runs[0].trigger == "follow_up_due"


class CollectingDispatcher:
    def __init__(self) -> None:
        self.run_ids: list[UUID] = []

    def enqueue_digital_worker_run(self, run_id: UUID) -> None:
        self.run_ids.append(run_id)


def _lead_response(
    *,
    gate_status: str = "passed",
    draft: DraftEmail | None = DraftEmail(
        subject="Leasing follow-up",
        body="Hi, worth comparing your inbound response motion this week?",
    ),
) -> LeadResponse:
    lead = LeadCreate(
        contact_name="Sample Contact",
        email="sample@operator.example",
        company="Multifamily Operator",
        role="VP Leasing",
        property_address="100 Main St",
        city="Austin",
        state="TX",
        country="US",
    )
    gates = GateResult(
        status=gate_status,
        failures=["test gate failed"] if gate_status == "failed" else [],
    )
    return LeadResponse(
        id=UUID("11111111-1111-4111-8111-111111111111"),
        input=lead,
        gates=gates,
        enrichment=demo_enrichment(lead.company, lead.city, lead.state),
        score=ScoreBreakdown(
            total=82,
            tier="A",
            company_fit=50,
            market_opportunity=30,
            bonuses=2,
            why_line="Strong inbound fit.",
            components={"company_fit": 50},
        ),
        talking_points=["Strong fit"],
        flags=[],
        draft=draft,
        related_leads=[],
        knowledge_graph=LeadKnowledgeGraph(),
        run_id=UUID("22222222-2222-4222-8222-222222222222"),
    )
