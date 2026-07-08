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
async def test_list_lead_queue_items_appends_loading_runs_without_duplicates() -> None:
    lead = _lead_response()
    duplicate_run = AgentRunResponse(
        run_id=UUID("22222222-3333-4333-8333-222222222222"),
        lead_id=LEAD_ID,
        status="queued",
        current_stage="queued",
    )
    loading_run = AgentRunResponse(
        run_id=UUID("22222222-4444-4444-8444-222222222222"),
        lead_id=UUID("11111111-2222-4222-8222-111111111111"),
        status="running",
        current_stage="agent_execution",
    )
    loading_input = LeadCreate(
        contact_name="Loading Contact",
        email="loading@sampleoperator.example",
        company="Loading Operator",
        role="VP Leasing",
        property_address="100 Main St",
        city="Austin",
        state="TX",
        country="US",
    )
    session = FakeSession(
        scalars=[
            [
                SimpleNamespace(
                    id=lead.id,
                    run_id=lead.run_id,
                    payload=lead.model_dump(mode="json"),
                )
            ],
            [
                SimpleNamespace(
                    lead_id=duplicate_run.lead_id,
                    run_id=duplicate_run.run_id,
                    input_payload=lead.input.model_dump(mode="json"),
                    payload=duplicate_run.model_dump(mode="json"),
                ),
                SimpleNamespace(
                    lead_id=loading_run.lead_id,
                    run_id=loading_run.run_id,
                    input_payload=loading_input.model_dump(mode="json"),
                    payload=loading_run.model_dump(mode="json"),
                ),
            ],
        ],
    )
    repository = SignalSnapshotRepository(session)

    items = await repository.list_lead_queue_items()

    assert [item.state for item in items] == ["ready", "loading"]
    assert items[0].lead == lead
    assert items[0].run is None
    assert items[1].lead is None
    assert items[1].run == loading_run
    assert items[1].input.contact_name == "Loading Contact"


@pytest.mark.asyncio
async def test_delete_lead_intelligence_counts_deleted_records() -> None:
    session = FakeSession(scalar_values=[0, 1, 2, 3])
    repository = SignalSnapshotRepository(session)

    result = await repository.delete_lead_intelligence(LEAD_ID)

    assert result.deleted_leads == 1
    assert result.deleted_agent_runs == 2
    assert result.deleted_status_events == 3
    assert result.skipped_assigned_leads == 0
    assert result.deleted_worker_assignments == 0
    assert len(session.executed_statements) == 3


@pytest.mark.asyncio
async def test_delete_lead_intelligence_skips_active_assignment() -> None:
    session = FakeSession(scalar_values=[1])
    repository = SignalSnapshotRepository(session)

    result = await repository.delete_lead_intelligence(LEAD_ID)

    assert result.deleted_leads == 0
    assert result.deleted_agent_runs == 0
    assert result.deleted_status_events == 0
    assert result.skipped_assigned_leads == 1
    assert session.executed_statements == []


@pytest.mark.asyncio
async def test_delete_lead_intelligence_can_include_worker_cleanup() -> None:
    session = FakeSession(scalar_values=[1, 2, 3, 4, 5, 1, 1, 1])
    repository = SignalSnapshotRepository(session)

    result = await repository.delete_lead_intelligence(
        LEAD_ID,
        include_digital_worker=True,
    )

    assert result.deleted_leads == 1
    assert result.deleted_agent_runs == 1
    assert result.deleted_status_events == 1
    assert result.skipped_assigned_leads == 0
    assert result.deleted_worker_assignments == 1
    assert result.deleted_worker_runs == 2
    assert result.deleted_worker_goal_states == 3
    assert result.deleted_worker_messages == 4
    assert result.deleted_worker_follow_ups == 5
    assert len(session.executed_statements) == 8


@pytest.mark.asyncio
async def test_delete_all_lead_intelligence_counts_skipped_assigned_leads() -> None:
    session = FakeSession(scalar_values=[2, 3, 4, 1])
    repository = SignalSnapshotRepository(session)

    result = await repository.delete_all_lead_intelligence()

    assert result.deleted_leads == 2
    assert result.deleted_agent_runs == 3
    assert result.deleted_status_events == 4
    assert result.skipped_assigned_leads == 1
    assert len(session.executed_statements) == 3


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
        self.executed_statements: list[object] = []

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
        self.executed_statements.append(statement)
        if not self.execute_values:
            return []
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
