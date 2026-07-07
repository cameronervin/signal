import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.executors.signal_pipeline import SignalPipelineExecutor
from app.core.config import Settings, get_settings
from app.infrastructure.db.session import (
    close_db_engine,
    get_sessionmaker,
)
from app.repositories.signal_snapshot import SignalSnapshotRepository
from app.services.agent_execution_service import AgentExecutionService
from app.services.lead_intake_service import LeadIntakeService
from scripts.demo_seed import DemoSeedPublicDataClient, demo_seed_records


async def seed_demo_leads(settings: Settings | None = None) -> int:
    app_settings = settings or get_settings()
    records = demo_seed_records()
    session_factory = get_sessionmaker(app_settings)
    async with session_factory.begin() as session:
        repository = SignalSnapshotRepository(session)
        execution_service = AgentExecutionService(
            repository,
            pipeline_executor=SignalPipelineExecutor(
                settings=app_settings,
                public_data_client=DemoSeedPublicDataClient(records),
            ),
        )
        service = LeadIntakeService(
            repository,
            agent_execution_service=execution_service,
        )
        seeded = [
            await service.create_and_enrich_with_ids(
                lead=record.lead,
                lead_id=record.lead_id,
                run_id=record.run_id,
                trigger="seed_script",
            )
            for record in records
        ]

    await close_db_engine(app_settings)
    print(f"Seeded {len(seeded)} example leads:")
    for lead in seeded:
        print(f"- {lead.id} / {lead.run_id}: tier {lead.score.tier}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(seed_demo_leads()))
