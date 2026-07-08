from types import SimpleNamespace
from uuid import UUID

import pytest

from app.agents.utils.scoring import score_lead
from app.infrastructure.public_data.fixtures import demo_enrichment
from app.models.signal import (
    SignalAgentRunRecord,
    SignalAgentRunStatusEventRecord,
    SignalLeadRecord,
)
from app.repositories.signal_snapshot import SignalSnapshotRepository
from app.schemas.lead import GateResult, LeadCreate, LeadResponse
from app.schemas.run import AgentRunResponse

LEAD_ID = UUID("11111111-1111-4111-8111-111111111111")
RUN_ID = UUID("22222222-2222-4222-8222-222222222222")


@pytest.mark.asyncio
async def test_save_lead_indexes_snapshot_fields() -> None:
    session = FakeSession()
    repository = SignalSnapshotRepository(session)
    lead = _lead_response()

    await repository.save_lead(lead)

    record = session.merged[0]
    assert isinstance(record, SignalLeadRecord)
    assert record.id == LEAD_ID
    assert record.run_id == RUN_ID
    assert record.tier == lead.score.tier
    assert record.score_total == lead.score.total
    assert record.market == "Austin, TX"
    assert record.gate_status == "passed"
    assert record.payload["id"] == str(LEAD_ID)


@pytest.mark.asyncio
async def test_save_agent_run_indexes_snapshot_fields() -> None:
    session = FakeSession()
    repository = SignalSnapshotRepository(session)
    run = AgentRunResponse(
        run_id=RUN_ID,
        lead_id=LEAD_ID,
        status="awaiting_review",
        trigger="api_insert",
        current_stage="human_review",
    )

    await repository.save_agent_run(run)

    record = session.added[0]
    assert isinstance(record, SignalAgentRunRecord)
    assert record.run_id == RUN_ID
    assert record.lead_id == LEAD_ID
    assert record.status == "awaiting_review"
    assert record.trigger == "api_insert"
    assert record.payload["current_stage"] == "human_review"
    assert isinstance(session.added[1], SignalAgentRunStatusEventRecord)


@pytest.mark.asyncio
async def test_create_queued_agent_run_stores_input_and_status_event() -> None:
    session = FakeSession()
    repository = SignalSnapshotRepository(session)
    lead = _lead_response().input
    run = AgentRunResponse(
        run_id=RUN_ID,
        lead_id=LEAD_ID,
        status="queued",
        trigger="api_insert",
        current_stage="queued",
    )

    await repository.create_queued_agent_run(
        run=run,
        lead=lead,
        task_id=RUN_ID,
    )

    record = session.merged[0]
    assert record.input_payload["email"] == str(lead.email)
    assert record.task_id == RUN_ID
    assert isinstance(session.added[0], SignalAgentRunStatusEventRecord)
    assert session.added[0].status == "queued"


@pytest.mark.asyncio
async def test_get_and_list_methods_validate_snapshot_payloads() -> None:
    lead = _lead_response()
    run = AgentRunResponse(
        run_id=RUN_ID,
        lead_id=LEAD_ID,
        status="awaiting_review",
        current_stage="human_review",
    )
    session = FakeSession(
        scalars=[
            [SimpleNamespace(payload=lead.model_dump(mode="json"))],
            [SimpleNamespace(payload=run.model_dump(mode="json"))],
        ],
        gets={
            (SignalLeadRecord, LEAD_ID): SimpleNamespace(
                payload=lead.model_dump(mode="json")
            ),
            (SignalAgentRunRecord, RUN_ID): SimpleNamespace(
                payload=run.model_dump(mode="json"),
                input_payload=lead.input.model_dump(mode="json"),
            ),
        },
    )
    repository = SignalSnapshotRepository(session)

    assert await repository.list_leads() == [lead]
    assert await repository.get_lead(LEAD_ID) == lead
    assert await repository.list_agent_runs() == [run]
    assert await repository.get_agent_run(RUN_ID) == run
    assert await repository.get_agent_run_input(RUN_ID) == lead.input


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
        gets: dict[tuple[type[object], object], object] | None = None,
        scalar_values: list[object] | None = None,
        execute_values: list[list[tuple[object, ...]]] | None = None,
    ) -> None:
        self.merged: list[object] = []
        self.added: list[object] = []
        self.scalars_results = scalars or []
        self.gets = gets or {}
        self.scalar_values = scalar_values or []
        self.execute_values = execute_values or []

    async def merge(self, record: object) -> None:
        self.merged.append(record)

    def add(self, record: object) -> None:
        self.added.append(record)

    async def commit(self) -> None:
        return None

    async def scalars(self, statement: object) -> list[object]:
        return self.scalars_results.pop(0)

    async def get(self, model: type[object], key: object) -> object | None:
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
        id=LEAD_ID,
        run_id=RUN_ID,
        input=lead,
        gates=gates,
        enrichment=enrichment,
        score=score_lead(lead, gates, enrichment),
    )
