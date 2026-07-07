import asyncio

from fastapi.testclient import TestClient

from app.agents.executors.signal_pipeline import SignalPipelineExecutor
from app.api.v1.dependencies import get_agent_run_service, get_analytics_service
from app.core.config import Settings
from app.main import create_app
from app.services.agent_execution_service import AgentExecutionService
from app.services.agent_run_service import AgentRunService
from app.services.analytics_service import AnalyticsService
from app.services.lead_intake_service import LeadIntakeService
from scripts.demo_seed import DemoSeedPublicDataClient, demo_seed_records
from tests.fakes import FakeSignalRepository


def test_agent_pause_approve_and_analytics_endpoints() -> None:
    records = demo_seed_records()
    repository = FakeSignalRepository()
    service = LeadIntakeService(
        repository,
        agent_execution_service=AgentExecutionService(
            repository,
            pipeline_executor=SignalPipelineExecutor(
                public_data_client=DemoSeedPublicDataClient(records)
            ),
        ),
    )
    asyncio.run(_seed_records(service, records))
    app = create_app(Settings(database_url="postgresql+asyncpg://invalid/unused"))

    async def override_agent_runs() -> AgentRunService:
        return AgentRunService(repository)

    async def override_analytics() -> AnalyticsService:
        return AnalyticsService(repository)

    app.dependency_overrides[get_agent_run_service] = override_agent_runs
    app.dependency_overrides[get_analytics_service] = override_analytics

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

        approved = client.post("/api/v1/agent-runs/run_seed_a/approve")
        assert approved.status_code == 200
        assert approved.json()["status"] == "completed"
        assert approved.json()["current_stage"] == "review_approved"
        assert "human_review: approved without send" in approved.json()["activity_log"]

        invalid_approval = client.post("/api/v1/agent-runs/run_seed_a/approve")
        assert invalid_approval.status_code == 409

        paused = client.post("/api/v1/agent-runs/run_seed_b/pause")
        assert paused.status_code == 200
        assert paused.json()["status"] == "paused"
        assert paused.json()["current_stage"] == "human_review_paused"

        invalid_pause = client.post("/api/v1/agent-runs/run_seed_gate_failed/pause")
        assert invalid_pause.status_code == 409


async def _seed_records(
    service: LeadIntakeService,
    records,
) -> None:
    for record in records:
        await service.create_and_enrich_with_ids(
            lead=record.lead,
            lead_id=record.lead_id,
            run_id=record.run_id,
            trigger="seed_script",
        )
