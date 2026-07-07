from types import SimpleNamespace

import pytest

from app.agents.utils.scoring import score_lead
from app.infrastructure.public_data.fixtures import demo_enrichment
from app.models.signal import SignalAgentRunRecord, SignalLeadRecord
from app.repositories.signal_snapshot import SignalSnapshotRepository
from app.schemas.lead import GateResult, LeadCreate, LeadResponse
from app.schemas.run import AgentRunResponse


@pytest.mark.asyncio
async def test_save_lead_indexes_snapshot_fields() -> None:
    session = FakeSession()
    repository = SignalSnapshotRepository(session)
    lead = _lead_response()

    await repository.save_lead(lead)

    record = session.merged[0]
    assert isinstance(record, SignalLeadRecord)
    assert record.id == "lead_test"
    assert record.run_id == "run_test"
    assert record.tier == lead.score.tier
    assert record.score_total == lead.score.total
    assert record.market == "Austin, TX"
    assert record.gate_status == "passed"
    assert record.payload["id"] == "lead_test"


@pytest.mark.asyncio
async def test_save_agent_run_indexes_snapshot_fields() -> None:
    session = FakeSession()
    repository = SignalSnapshotRepository(session)
    run = AgentRunResponse(
        run_id="run_test",
        lead_id="lead_test",
        status="awaiting_review",
        trigger="api_insert",
        current_stage="human_review",
    )

    await repository.save_agent_run(run)

    record = session.merged[0]
    assert isinstance(record, SignalAgentRunRecord)
    assert record.run_id == "run_test"
    assert record.lead_id == "lead_test"
    assert record.status == "awaiting_review"
    assert record.trigger == "api_insert"
    assert record.payload["current_stage"] == "human_review"


@pytest.mark.asyncio
async def test_get_and_list_methods_validate_snapshot_payloads() -> None:
    lead = _lead_response()
    run = AgentRunResponse(
        run_id="run_test",
        lead_id="lead_test",
        status="awaiting_review",
        current_stage="human_review",
    )
    session = FakeSession(
        scalars=[
            [SimpleNamespace(payload=lead.model_dump(mode="json"))],
            [SimpleNamespace(payload=run.model_dump(mode="json"))],
        ],
        gets={
            (SignalLeadRecord, "lead_test"): SimpleNamespace(
                payload=lead.model_dump(mode="json")
            ),
            (SignalAgentRunRecord, "run_test"): SimpleNamespace(
                payload=run.model_dump(mode="json")
            ),
        },
    )
    repository = SignalSnapshotRepository(session)

    assert await repository.list_leads() == [lead]
    assert await repository.get_lead("lead_test") == lead
    assert await repository.list_agent_runs() == [run]
    assert await repository.get_agent_run("run_test") == run


@pytest.mark.asyncio
async def test_analytics_summary_maps_aggregate_rows() -> None:
    session = FakeSession(
        scalars=[[], []],
        scalar_values=[6, 67.5, 5, 1],
        execute_values=[
            [("A", 2), ("B", 2), ("C", 2)],
            [("Austin, TX", 2), ("Denver, CO", 1)],
        ],
    )
    repository = SignalSnapshotRepository(session)

    summary = await repository.analytics_summary()

    assert summary.total_leads == 6
    assert summary.tier_distribution == {"A": 2, "B": 2, "C": 2}
    assert summary.awaiting_review_count == 5
    assert summary.gate_failed_count == 1
    assert summary.average_score == 67.5
    assert [market.market for market in summary.top_markets] == [
        "Austin, TX",
        "Denver, CO",
    ]


class FakeSession:
    def __init__(
        self,
        *,
        scalars: list[list[object]] | None = None,
        gets: dict[tuple[type[object], str], object] | None = None,
        scalar_values: list[object] | None = None,
        execute_values: list[list[tuple[object, ...]]] | None = None,
    ) -> None:
        self.merged: list[object] = []
        self.scalars_results = scalars or []
        self.gets = gets or {}
        self.scalar_values = scalar_values or []
        self.execute_values = execute_values or []

    async def merge(self, record: object) -> None:
        self.merged.append(record)

    async def scalars(self, statement: object) -> list[object]:
        return self.scalars_results.pop(0)

    async def get(self, model: type[object], key: str) -> object | None:
        return self.gets.get((model, key))

    async def scalar(self, statement: object) -> object:
        return self.scalar_values.pop(0)

    async def execute(self, statement: object) -> list[tuple[object, ...]]:
        return self.execute_values.pop(0)


def _lead_response() -> LeadResponse:
    lead = LeadCreate(
        contact_name="Sample Contact",
        email="lead@sampleoperator.example",
        company="Sample Multifamily Group",
        role="VP Leasing",
        property_address="100 Main St",
        city="Austin",
        state="TX",
        country="US",
    )
    gates = GateResult(status="passed")
    enrichment = demo_enrichment(lead.company, lead.city, lead.state)
    return LeadResponse(
        id="lead_test",
        run_id="run_test",
        input=lead,
        gates=gates,
        enrichment=enrichment,
        score=score_lead(lead, gates, enrichment),
    )
