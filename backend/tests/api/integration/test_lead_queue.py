from uuid import UUID

from fastapi.testclient import TestClient

from app.api.v1.dependencies import get_lead_intake_service
from app.core.config import Settings
from app.main import create_app
from app.services.agent_execution_service import AgentExecutionService
from app.services.lead_intake_service import LeadIntakeService
from tests.fakes import FakeSignalRepository


def test_create_lead_queues_agent_run_with_uuid_ids() -> None:
    repository = FakeSignalRepository()
    dispatcher = FakeDispatcher()
    app = create_app(Settings(database_url="postgresql+asyncpg://invalid/unused"))

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


class FakeDispatcher:
    def __init__(self) -> None:
        self.run_ids: list[UUID] = []

    def enqueue_agent_run(self, run_id: UUID) -> None:
        self.run_ids.append(run_id)
