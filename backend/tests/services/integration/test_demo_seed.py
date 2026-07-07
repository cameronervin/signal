import json
import subprocess
import sys
from pathlib import Path

import pytest

from app.agents.executors.signal_pipeline import SignalPipelineExecutor
from app.core.config import Settings
from app.services.agent_execution_service import AgentExecutionService
from app.services.lead_intake_service import LeadIntakeService
from scripts.demo_seed import DemoSeedPublicDataClient, demo_seed_records
from scripts.seed_demo_leads import seed_demo_leads
from tests.fakes import FakeSignalRepository

PERSISTENT_SEED_FORBIDDEN_TERMS = (
    "demo",
    "Demo",
    "fixture",
    "fixture history",
    "Example:",
    ".example",
)


def test_database_and_llm_imports_do_not_cycle() -> None:
    backend_dir = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from app.infrastructure.db.base import Base; "
                "from app.infrastructure.llm.factory import get_llm_provider; "
                "print(Base.__name__, callable(get_llm_provider))"
            ),
        ],
        cwd=backend_dir,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Base True"


@pytest.mark.asyncio
async def test_demo_seed_records_are_stable_and_idempotent() -> None:
    records = demo_seed_records()
    repository = FakeSignalRepository()
    service = _lead_service(
        repository,
        SignalPipelineExecutor(
            public_data_client=DemoSeedPublicDataClient(records),
        ),
    )

    first_pass = await _seed_records(service, records)
    second_pass = await _seed_records(service, records)
    leads = await service.list_leads()

    assert len(first_pass) == 6
    assert len(second_pass) == 6
    assert len(leads) == 6
    assert [lead.id for lead in leads] == [
        "lead_seed_a",
        "lead_seed_missing_trigger",
        "lead_seed_warning_only",
        "lead_seed_b",
        "lead_seed_c",
        "lead_seed_gate_failed",
    ]
    assert {lead.score.tier for lead in leads} == {"A", "B", "C"}
    assert {lead.input.contact_name for lead in leads} == {
        "Andrew Ng",
        "Demis Hassabis",
        "Fei-Fei Li",
        "Geoffrey Hinton",
        "Yann LeCun",
        "Yoshua Bengio",
    }
    assert {str(lead.input.email) for lead in leads} == {
        "andrew.ng@metrocommunitiesgroup.com",
        "demis.hassabis@gmail.com",
        "fei-fei.li@portfoliohousinggroup.com",
        "geoffrey.hinton@regionalresidentialgroup.com",
        "yann.lecun@localhousingoperator.com",
        "yoshua.bengio@smalloperatorcollective.com",
    }
    assert all(
        any(
            source.source == "OpenStreetMap Nominatim"
            for source in lead.enrichment.sources
        )
        for lead in leads
    )
    assert all(
        any(source.label == "Household count" for source in lead.enrichment.sources)
        for lead in leads
    )
    gate_failed = await service.get_lead("lead_seed_gate_failed")
    assert gate_failed is not None
    assert gate_failed.gates.status == "failed"
    assert gate_failed.draft is None
    warning_only = await service.get_lead("lead_seed_warning_only")
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
        def begin(self) -> "FakeSessionContext":
            return self

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
        "scripts.seed_demo_leads.SignalSnapshotRepository",
        lambda session: repository,
    )

    exit_code = await seed_demo_leads(
        Settings(database_url="postgresql+asyncpg://postgres:test/db")
    )

    assert exit_code == 0
    assert "Seeded 6 example leads" in capsys.readouterr().out
    assert len(await repository.list_leads()) == 6
    assert len(await repository.list_agent_runs()) == 6
    runs = await repository.list_agent_runs()
    assert all(run.trigger == "seed_script" for run in runs)


@pytest.mark.asyncio
async def test_seeded_payloads_do_not_persist_demo_or_fixture_language() -> None:
    records = demo_seed_records()
    repository = FakeSignalRepository()
    service = _lead_service(
        repository,
        SignalPipelineExecutor(
            public_data_client=DemoSeedPublicDataClient(records),
        ),
    )

    await _seed_records(service, records)
    payload = json.dumps(
        {
            "leads": [
                lead.model_dump(mode="json") for lead in await repository.list_leads()
            ],
            "runs": [
                run.model_dump(mode="json")
                for run in await repository.list_agent_runs()
            ],
        },
        sort_keys=True,
    )

    for term in PERSISTENT_SEED_FORBIDDEN_TERMS:
        assert term not in payload


def _lead_service(
    repository: FakeSignalRepository,
    pipeline_executor: SignalPipelineExecutor,
) -> LeadIntakeService:
    return LeadIntakeService(
        repository,
        agent_execution_service=AgentExecutionService(
            repository,
            pipeline_executor=pipeline_executor,
        ),
    )


async def _seed_records(
    service: LeadIntakeService,
    records,
):
    return [
        await service.create_and_enrich_with_ids(
            lead=record.lead,
            lead_id=record.lead_id,
            run_id=record.run_id,
            trigger="seed_script",
        )
        for record in records
    ]
