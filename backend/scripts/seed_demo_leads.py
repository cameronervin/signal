import asyncio
import sys
from pathlib import Path
from time import monotonic

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import Settings, get_settings
from app.infrastructure.db.session import (
    close_db_engine,
    get_sessionmaker,
)
from app.repositories.signal_snapshot import SignalSnapshotRepository
from app.services.agent_execution_service import AgentExecutionService
from app.services.lead_intake_service import LeadIntakeService
from scripts.demo_seed import demo_seed_records


async def seed_demo_leads(
    settings: Settings | None = None,
    *,
    timeout_seconds: float = 60.0,
    poll_interval_seconds: float = 1.0,
) -> int:
    app_settings = settings or get_settings()
    records = demo_seed_records()
    session_factory = get_sessionmaker(app_settings)
    async with session_factory() as session:
        repository = SignalSnapshotRepository(session)
        service = LeadIntakeService(
            repository,
            agent_execution_service=AgentExecutionService(repository),
        )
        queued = [
            await service.create_and_enqueue_with_ids(
                lead=record.lead,
                lead_id=record.lead_id,
                run_id=record.run_id,
                trigger="seed_script",
            )
            for record in records
        ]

    print(f"Queued {len(queued)} example lead agent run(s):")
    for run in queued:
        print(f"- {run.lead_id} / {run.run_id}: {run.status}")

    deadline = monotonic() + timeout_seconds
    seeded = []
    while monotonic() <= deadline:
        async with session_factory() as session:
            repository = SignalSnapshotRepository(session)
            seeded = [
                lead
                for lead in await repository.list_leads()
                if lead.id in {record.lead_id for record in records}
            ]
        if len(seeded) == len(records):
            break
        await asyncio.sleep(poll_interval_seconds)

    await close_db_engine(app_settings)
    if len(seeded) != len(records):
        print(
            "Timed out waiting for queued seed runs to complete. "
            "Start the Celery worker and rerun the seed script."
        )
        return 1

    print(f"Completed {len(seeded)} example leads:")
    for lead in seeded:
        print(f"- {lead.id} / {lead.run_id}: tier {lead.score.tier}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(seed_demo_leads()))
