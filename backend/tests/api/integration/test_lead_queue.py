import asyncio
from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.agents.utils.scoring import score_lead
from app.api.v1.dependencies import get_agent_run_service, get_lead_intake_service
from app.api.v1.router import api_router
from app.infrastructure.public_data.fixtures import demo_enrichment
from app.schemas.lead import GateResult, LeadCreate, LeadResponse
from app.schemas.run import AgentRunResponse
from app.services.agent_execution_service import AgentExecutionService
from app.services.agent_run_service import AgentRunService
from app.services.lead_intake_service import LeadIntakeService
from tests.fakes import FakeSignalRepository

READY_LEAD_ID = UUID("11111111-1111-4111-8111-111111111111")
READY_RUN_ID = UUID("21111111-1111-4111-8111-111111111111")
LOADING_LEAD_ID = UUID("11111111-2222-4222-8222-111111111111")
LOADING_RUN_ID = UUID("21111111-2222-4222-8222-111111111111")
OTHER_READY_LEAD_ID = UUID("11111111-3333-4333-8333-111111111111")
OTHER_READY_RUN_ID = UUID("21111111-3333-4333-8333-111111111111")


def test_create_lead_queues_agent_run_with_uuid_ids() -> None:
    repository = FakeSignalRepository()
    dispatcher = FakeDispatcher()
    app = _test_app()

    async def override_lead_service() -> LeadIntakeService:
        return LeadIntakeService(
            repository,
            agent_execution_service=AgentExecutionService(repository),
            task_dispatcher=dispatcher,
        )

    app.dependency_overrides[get_lead_intake_service] = override_lead_service

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/leads",
            json={
                "contact_name": "Sample Contact",
                "email": "contact@operator.example",
                "company": "Multifamily Operator",
                "role": "VP Leasing",
                "property_address": "100 Main St",
                "city": "Austin",
                "state": "TX",
                "country": "US",
            },
        )

    assert response.status_code == 202
    body = response.json()
    lead_id = UUID(body["lead_id"])
    run_id = UUID(body["run_id"])
    assert body["status"] == "queued"
    assert body["current_stage"] == "queued"
    assert dispatcher.run_ids == [run_id]
    assert repository.commits == 1
    assert repository._runs[run_id].lead_id == lead_id
    assert repository._run_inputs[run_id].company == "Multifamily Operator"


def test_lead_queue_shows_ready_rows_before_loading_runs() -> None:
    repository = FakeSignalRepository()
    execution_service = AgentExecutionService(repository)
    app = _test_app()

    async def override_lead_service() -> LeadIntakeService:
        return LeadIntakeService(
            repository,
            agent_execution_service=execution_service,
            task_dispatcher=FakeDispatcher(),
        )

    app.dependency_overrides[get_lead_intake_service] = override_lead_service
    ready_lead = _lead_response(
        lead_id=READY_LEAD_ID,
        run_id=READY_RUN_ID,
        contact_name="Ready Contact",
        company="Ready Operator",
    )
    loading_input = _lead_input(
        contact_name="Loading Contact",
        company="Loading Operator",
    )
    loading_run = execution_service.build_queued_run_response(
        lead_id=LOADING_LEAD_ID,
        run_id=LOADING_RUN_ID,
        trigger="api_insert",
    )

    async def seed_repository() -> None:
        await repository.save_lead(ready_lead)
        await repository.create_queued_agent_run(
            run=loading_run,
            lead=loading_input,
            task_id=loading_run.run_id,
        )

    asyncio.run(seed_repository())

    with TestClient(app) as client:
        queue = client.get("/api/v1/leads/queue")
        completed = client.get("/api/v1/leads")

    assert queue.status_code == 200
    assert completed.status_code == 200
    assert [item["state"] for item in queue.json()] == ["ready", "loading"]
    assert queue.json()[0]["lead"]["input"]["contact_name"] == "Ready Contact"
    assert queue.json()[1]["lead"] is None
    assert queue.json()[1]["run"]["status"] == "queued"
    assert queue.json()[1]["input"]["contact_name"] == "Loading Contact"
    assert [lead["input"]["contact_name"] for lead in completed.json()] == [
        "Ready Contact"
    ]


def test_delete_lead_removes_ready_lead_queue_row_and_agent_run() -> None:
    repository = FakeSignalRepository()
    execution_service = AgentExecutionService(repository)
    app = _test_app()
    _override_services(app, repository, execution_service)
    ready_lead = _lead_response(
        lead_id=READY_LEAD_ID,
        run_id=READY_RUN_ID,
        contact_name="Ready Contact",
        company="Ready Operator",
    )
    ready_run = AgentRunResponse(
        lead_id=READY_LEAD_ID,
        run_id=READY_RUN_ID,
        status="awaiting_review",
        trigger="api_insert",
        current_stage="human_review",
    )

    async def seed_repository() -> None:
        await repository.save_lead(ready_lead)
        await repository.save_agent_run(ready_run)

    asyncio.run(seed_repository())

    with TestClient(app) as client:
        deleted = client.delete(f"/api/v1/leads/{READY_LEAD_ID}")
        queue = client.get("/api/v1/leads/queue")
        completed = client.get("/api/v1/leads")
        runs = client.get("/api/v1/agent-runs")

    assert deleted.status_code == 200
    assert deleted.json() == {
        "deleted_leads": 1,
        "deleted_agent_runs": 1,
        "deleted_status_events": 1,
        "skipped_assigned_leads": 0,
        "deleted_worker_assignments": 0,
        "deleted_worker_runs": 0,
        "deleted_worker_goal_states": 0,
        "deleted_worker_messages": 0,
        "deleted_worker_follow_ups": 0,
    }
    assert queue.json() == []
    assert completed.json() == []
    assert runs.json() == []


def test_delete_lead_removes_loading_queue_row() -> None:
    repository = FakeSignalRepository()
    execution_service = AgentExecutionService(repository)
    app = _test_app()
    _override_services(app, repository, execution_service)
    loading_run = execution_service.build_queued_run_response(
        lead_id=LOADING_LEAD_ID,
        run_id=LOADING_RUN_ID,
        trigger="api_insert",
    )

    async def seed_repository() -> None:
        await repository.create_queued_agent_run(
            run=loading_run,
            lead=_lead_input(
                contact_name="Loading Contact",
                company="Loading Operator",
            ),
            task_id=loading_run.run_id,
        )

    asyncio.run(seed_repository())

    with TestClient(app) as client:
        deleted = client.delete(f"/api/v1/leads/{LOADING_LEAD_ID}")
        queue = client.get("/api/v1/leads/queue")

    assert deleted.status_code == 200
    assert deleted.json()["deleted_leads"] == 0
    assert deleted.json()["deleted_agent_runs"] == 1
    assert deleted.json()["deleted_status_events"] == 1
    assert queue.json() == []


def test_delete_lead_returns_404_for_missing_lead_intelligence() -> None:
    repository = FakeSignalRepository()
    execution_service = AgentExecutionService(repository)
    app = _test_app()
    _override_services(app, repository, execution_service)

    with TestClient(app) as client:
        response = client.delete(f"/api/v1/leads/{READY_LEAD_ID}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Lead not found"


def test_delete_lead_returns_409_for_active_worker_assignment() -> None:
    repository = FakeSignalRepository()
    execution_service = AgentExecutionService(repository)
    app = _test_app()
    _override_services(app, repository, execution_service)
    repository.active_assignment_lead_ids.add(READY_LEAD_ID)

    with TestClient(app) as client:
        response = client.delete(f"/api/v1/leads/{READY_LEAD_ID}")

    assert response.status_code == 409
    assert "Digital Workforce assignment" in response.json()["detail"]


def test_delete_lead_includes_worker_cleanup_when_requested() -> None:
    repository = FakeSignalRepository()
    execution_service = AgentExecutionService(repository)
    app = _test_app()
    _override_services(app, repository, execution_service)
    repository.active_assignment_lead_ids.add(READY_LEAD_ID)
    repository.worker_cleanup_counts_by_lead[READY_LEAD_ID] = {
        "assignments": 1,
        "runs": 2,
        "goal_states": 7,
        "messages": 1,
        "follow_ups": 1,
    }
    ready_lead = _lead_response(
        lead_id=READY_LEAD_ID,
        run_id=READY_RUN_ID,
        contact_name="Ready Contact",
        company="Ready Operator",
    )
    ready_run = AgentRunResponse(
        lead_id=READY_LEAD_ID,
        run_id=READY_RUN_ID,
        status="awaiting_review",
        trigger="api_insert",
        current_stage="human_review",
    )

    async def seed_repository() -> None:
        await repository.save_lead(ready_lead)
        await repository.save_agent_run(ready_run)

    asyncio.run(seed_repository())

    with TestClient(app) as client:
        deleted = client.delete(
            f"/api/v1/leads/{READY_LEAD_ID}?include_digital_worker=true"
        )
        queue = client.get("/api/v1/leads/queue")
        runs = client.get("/api/v1/agent-runs")

    assert deleted.status_code == 200
    assert deleted.json() == {
        "deleted_leads": 1,
        "deleted_agent_runs": 1,
        "deleted_status_events": 1,
        "skipped_assigned_leads": 0,
        "deleted_worker_assignments": 1,
        "deleted_worker_runs": 2,
        "deleted_worker_goal_states": 7,
        "deleted_worker_messages": 1,
        "deleted_worker_follow_ups": 1,
    }
    assert queue.json() == []
    assert runs.json() == []
    assert READY_LEAD_ID not in repository.active_assignment_lead_ids


def test_delete_all_leads_skips_assigned_leads() -> None:
    repository = FakeSignalRepository()
    execution_service = AgentExecutionService(repository)
    app = _test_app()
    _override_services(app, repository, execution_service)
    repository.active_assignment_lead_ids.add(READY_LEAD_ID)
    blocked_lead = _lead_response(
        lead_id=READY_LEAD_ID,
        run_id=READY_RUN_ID,
        contact_name="Blocked Contact",
        company="Blocked Operator",
    )
    deletable_lead = _lead_response(
        lead_id=OTHER_READY_LEAD_ID,
        run_id=OTHER_READY_RUN_ID,
        contact_name="Deletable Contact",
        company="Deletable Operator",
    )

    async def seed_repository() -> None:
        await repository.save_lead(blocked_lead)
        await repository.save_agent_run(
            AgentRunResponse(
                lead_id=blocked_lead.id,
                run_id=blocked_lead.run_id,
                status="awaiting_review",
                trigger="api_insert",
                current_stage="human_review",
            )
        )
        await repository.save_lead(deletable_lead)
        await repository.save_agent_run(
            AgentRunResponse(
                lead_id=deletable_lead.id,
                run_id=deletable_lead.run_id,
                status="completed",
                trigger="api_insert",
                current_stage="complete",
            )
        )

    asyncio.run(seed_repository())

    with TestClient(app) as client:
        deleted = client.delete("/api/v1/leads")
        completed = client.get("/api/v1/leads")
        runs = client.get("/api/v1/agent-runs")

    assert deleted.status_code == 200
    assert deleted.json() == {
        "deleted_leads": 1,
        "deleted_agent_runs": 1,
        "deleted_status_events": 1,
        "skipped_assigned_leads": 1,
        "deleted_worker_assignments": 0,
        "deleted_worker_runs": 0,
        "deleted_worker_goal_states": 0,
        "deleted_worker_messages": 0,
        "deleted_worker_follow_ups": 0,
    }
    assert [lead["id"] for lead in completed.json()] == [str(READY_LEAD_ID)]
    assert [run["lead_id"] for run in runs.json()] == [str(READY_LEAD_ID)]


class FakeDispatcher:
    def __init__(self) -> None:
        self.run_ids: list[UUID] = []

    def enqueue_agent_run(self, run_id: UUID) -> None:
        self.run_ids.append(run_id)


def _test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")
    return app


def _override_services(
    app: FastAPI,
    repository: FakeSignalRepository,
    execution_service: AgentExecutionService,
) -> None:
    async def override_lead_service() -> LeadIntakeService:
        return LeadIntakeService(
            repository,
            agent_execution_service=execution_service,
            task_dispatcher=FakeDispatcher(),
        )

    async def override_agent_run_service() -> AgentRunService:
        return AgentRunService(repository)

    app.dependency_overrides[get_lead_intake_service] = override_lead_service
    app.dependency_overrides[get_agent_run_service] = override_agent_run_service


def _lead_input(
    *,
    contact_name: str,
    company: str,
) -> LeadCreate:
    return LeadCreate(
        contact_name=contact_name,
        email=f"{contact_name.lower().replace(' ', '.')}@operator.example",
        company=company,
        role="VP Leasing",
        property_address="100 Main St",
        city="Austin",
        state="TX",
        country="US",
    )


def _lead_response(
    *,
    lead_id: UUID,
    run_id: UUID,
    contact_name: str,
    company: str,
) -> LeadResponse:
    lead = _lead_input(contact_name=contact_name, company=company)
    gates = GateResult(status="passed")
    enrichment = demo_enrichment(lead.company, lead.city, lead.state)
    return LeadResponse(
        id=lead_id,
        run_id=run_id,
        input=lead,
        gates=gates,
        enrichment=enrichment,
        score=score_lead(lead, gates, enrichment),
    )
