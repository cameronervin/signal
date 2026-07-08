import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.dependencies import get_digital_worker_service
from app.api.v1.router import api_router
from app.schemas.digital_worker import DigitalWorkerAssignmentCreate
from app.services.digital_worker_service import DigitalWorkerService
from tests.fakes import FakeDigitalWorkerRepository, FakeSignalRepository
from tests.services.unit.test_digital_worker_service import (
    CollectingDispatcher,
    _lead_response,
)


def test_digital_workforce_assignment_endpoint_returns_queued_assignment() -> None:
    signal_repository = FakeSignalRepository()
    worker_repository = FakeDigitalWorkerRepository()
    dispatcher = CollectingDispatcher()
    lead = _lead_response()
    asyncio.run(signal_repository.save_lead(lead))
    service = DigitalWorkerService(
        signal_repository=signal_repository,
        worker_repository=worker_repository,
        task_dispatcher=dispatcher,
    )
    app = _test_app()

    async def override_digital_worker_service() -> DigitalWorkerService:
        return service

    app.dependency_overrides[get_digital_worker_service] = (
        override_digital_worker_service
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/digital-workforce/assignments",
            json=DigitalWorkerAssignmentCreate(lead_id=lead.id).model_dump(
                mode="json"
            ),
        )

    assert response.status_code == 202
    body = response.json()
    assert body["lead_id"] == str(lead.id)
    assert body["status"] == "active"
    assert body["latest_run_id"] == str(dispatcher.run_ids[0])


def test_digital_workforce_rejects_missing_assignment_detail() -> None:
    service = DigitalWorkerService(
        signal_repository=FakeSignalRepository(),
        worker_repository=FakeDigitalWorkerRepository(),
        task_dispatcher=CollectingDispatcher(),
    )
    app = _test_app()

    async def override_digital_worker_service() -> DigitalWorkerService:
        return service

    app.dependency_overrides[get_digital_worker_service] = (
        override_digital_worker_service
    )

    with TestClient(app) as client:
        response = client.get(
            "/api/v1/digital-workforce/assignments/"
            "11111111-1111-4111-8111-111111111111"
        )

    assert response.status_code == 404


def _test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")
    return app
