import pytest

from app.agents.executors.signal_pipeline import SignalPipelineExecutor
from app.core.config import Settings
from app.services.demo_seed import DemoSeedPublicDataClient, demo_seed_records
from app.services.lead_service import LeadService
from scripts.seed_demo_leads import seed_demo_leads
from tests.fakes import FakeSignalRepository


@pytest.mark.asyncio
async def test_demo_seed_records_are_stable_and_idempotent() -> None:
    records = demo_seed_records()
    service = LeadService(
        FakeSignalRepository(),
        pipeline_executor=SignalPipelineExecutor(
            public_data_client=DemoSeedPublicDataClient(records)
        ),
    )

    first_pass = await service.seed_demo_records(records)
    second_pass = await service.seed_demo_records(records)
    leads = await service.list_leads()

    assert len(first_pass) == 6
    assert len(second_pass) == 6
    assert len(leads) == 6
    assert [lead.id for lead in leads] == [
        "lead_demo_a",
        "lead_demo_missing_trigger",
        "lead_demo_warning_only",
        "lead_demo_b",
        "lead_demo_c",
        "lead_demo_gate_failed",
    ]
    assert {lead.score.tier for lead in leads} == {"A", "B", "C"}
    gate_failed = await service.get_lead("lead_demo_gate_failed")
    assert gate_failed is not None
    assert gate_failed.gates.status == "failed"
    assert gate_failed.draft is None
    warning_only = await service.get_lead("lead_demo_warning_only")
    assert warning_only is not None
    assert warning_only.gates.status == "passed"
    assert warning_only.gates.warnings == ["sub-scale portfolio"]


@pytest.mark.asyncio
async def test_seed_script_writes_demo_records_through_postgres_repository(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    repository = FakeSignalRepository()

    class FakeSessionContext:
        def __call__(self) -> "FakeSessionContext":
            return self

        async def __aenter__(self) -> object:
            return object()

        async def __aexit__(self, *args: object) -> None:
            return None

    def fake_sessionmaker(settings: Settings) -> FakeSessionContext:
        assert settings.database_url == "postgresql+asyncpg://postgres:test/db"
        return FakeSessionContext()

    monkeypatch.setattr("scripts.seed_demo_leads.get_sessionmaker", fake_sessionmaker)
    monkeypatch.setattr(
        "scripts.seed_demo_leads.PostgresSignalRepository",
        lambda session: repository,
    )

    exit_code = await seed_demo_leads(
        Settings(database_url="postgresql+asyncpg://postgres:test/db")
    )

    assert exit_code == 0
    assert "Seeded 6 demo leads" in capsys.readouterr().out
    assert len(await repository.list_leads()) == 6
