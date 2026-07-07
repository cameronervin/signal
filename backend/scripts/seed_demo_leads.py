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
from app.repositories.postgres import PostgresSignalRepository
from app.services.demo_seed import DemoSeedPublicDataClient, demo_seed_records
from app.services.lead_service import LeadService


async def seed_demo_leads(settings: Settings | None = None) -> int:
    app_settings = settings or get_settings()
    records = demo_seed_records()
    session_factory = get_sessionmaker(app_settings)
    async with session_factory() as session:
        service = LeadService(
            PostgresSignalRepository(session),
            pipeline_executor=SignalPipelineExecutor(
                settings=app_settings,
                public_data_client=DemoSeedPublicDataClient(records),
            ),
        )
        seeded = await service.seed_demo_records(records)

    await close_db_engine(app_settings)
    print(f"Seeded {len(seeded)} demo leads:")
    for lead in seeded:
        print(f"- {lead.id} / {lead.run_id}: tier {lead.score.tier}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(seed_demo_leads()))
