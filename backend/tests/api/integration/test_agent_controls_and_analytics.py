import asyncio

from fastapi.testclient import TestClient

from app.agents.executors.signal_pipeline import SignalPipelineExecutor
from app.core.config import Settings
from app.main import create_app
from app.services.demo_seed import DemoSeedPublicDataClient, demo_seed_records
from app.services.lead_service import LeadService, get_lead_service
from tests.fakes import FakeSignalRepository


def test_agent_pause_approve_and_analytics_endpoints() -> None:
    records = demo_seed_records()
    service = LeadService(
        FakeSignalRepository(),
        pipeline_executor=SignalPipelineExecutor(
            public_data_client=DemoSeedPublicDataClient(records)
        ),
    )
    asyncio.run(service.seed_demo_records(records))
    app = create_app(Settings(database_url="postgresql+asyncpg://invalid/unused"))

    async def override_service() -> LeadService:
        return service

    app.dependency_overrides[get_lead_service] = override_service

    with TestClient(app) as client:
        summary = client.get("/api/v1/analytics/summary")
        assert summary.status_code == 200
        assert summary.json() == {
            "total_leads": 6,
            "tier_distribution": {"A": 2, "B": 2, "C": 2},
            "awaiting_review_count": 5,
            "gate_failed_count": 1,
            "average_score": 67.5,
            "top_markets": [
                {"market": "Austin, TX", "lead_count": 2},
                {"market": "Charlotte, NC", "lead_count": 1},
                {"market": "Denver, CO", "lead_count": 1},
                {"market": "Toledo, OH", "lead_count": 1},
                {"market": "Miami, FL", "lead_count": 1},
            ],
        }

        approved = client.post("/api/v1/agent-runs/run_demo_a/approve")
        assert approved.status_code == 200
        assert approved.json()["status"] == "completed"
        assert approved.json()["current_stage"] == "review_approved"
        assert "human_review: approved without send" in approved.json()["activity_log"]

        invalid_approval = client.post("/api/v1/agent-runs/run_demo_a/approve")
        assert invalid_approval.status_code == 409

        paused = client.post("/api/v1/agent-runs/run_demo_b/pause")
        assert paused.status_code == 200
        assert paused.json()["status"] == "paused"
        assert paused.json()["current_stage"] == "human_review_paused"

        invalid_pause = client.post("/api/v1/agent-runs/run_demo_gate_failed/pause")
        assert invalid_pause.status_code == 409
