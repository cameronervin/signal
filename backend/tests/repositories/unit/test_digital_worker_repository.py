from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.models.signal import DigitalWorkerAssignmentRecord, DigitalWorkerRunRecord
from app.repositories.digital_worker import DigitalWorkerPostgresRepository


@pytest.mark.asyncio
async def test_update_assignment_state_refreshes_assignment_before_response() -> None:
    assignment_id = uuid4()
    record = DigitalWorkerAssignmentRecord(
        assignment_id=assignment_id,
        lead_id=uuid4(),
        status="active",
        current_phase="initial_outreach",
        lifecycle_version="test",
        latest_run_id=None,
        payload={"activity_log": []},
    )
    session = _AssignmentUpdateSession(record)
    repository = DigitalWorkerPostgresRepository(session)
    response = object()

    async def assignment_response(updated_record: DigitalWorkerAssignmentRecord):
        assert session.refreshed_record is updated_record
        return response

    repository._assignment_response = assignment_response  # type: ignore[method-assign]

    result = await repository.update_assignment_state(
        assignment_id=assignment_id,
        current_phase="reply_qualification",
        activity="worker: phase advanced",
    )

    assert result is response
    assert session.flushed is True
    assert session.refreshed_record is record


@pytest.mark.asyncio
async def test_update_run_status_clears_failed_timestamp_after_replay_success() -> None:
    assignment = DigitalWorkerAssignmentRecord(
        assignment_id=uuid4(),
        lead_id=uuid4(),
        status="active",
        current_phase="reply_qualification",
        lifecycle_version="test",
        latest_run_id=None,
        payload={"activity_log": []},
    )
    run = DigitalWorkerRunRecord(
        run_id=uuid4(),
        assignment_id=assignment.assignment_id,
        trigger="assignment_created",
        status="failed",
        current_phase="reply_qualification",
        message="digital worker execution failed",
        payload=None,
        failed_at=datetime(2026, 7, 8, tzinfo=UTC),
    )
    session = _RunStatusSession(run, assignment)
    repository = DigitalWorkerPostgresRepository(session)

    result = await repository.update_run_status(
        run_id=run.run_id,
        status="completed",
        message="digital worker completed one wake-up",
    )

    assert result is not None
    assert result.status == "completed"
    assert result.failed_at is None
    assert result.completed_at is not None
    assert run.failed_at is None
    assert run.completed_at is not None
    assert session.flushed is True


class _AssignmentUpdateSession:
    def __init__(self, record: DigitalWorkerAssignmentRecord) -> None:
        self.record = record
        self.flushed = False
        self.refreshed_record: DigitalWorkerAssignmentRecord | None = None

    async def get(
        self,
        model: type[DigitalWorkerAssignmentRecord],
        primary_key,
    ) -> DigitalWorkerAssignmentRecord | None:
        if (
            model is DigitalWorkerAssignmentRecord
            and primary_key == self.record.assignment_id
        ):
            return self.record
        return None

    async def flush(self) -> None:
        self.flushed = True

    async def refresh(self, record: DigitalWorkerAssignmentRecord) -> None:
        self.refreshed_record = record


class _RunStatusSession:
    def __init__(
        self,
        run: DigitalWorkerRunRecord,
        assignment: DigitalWorkerAssignmentRecord,
    ) -> None:
        self.run = run
        self.assignment = assignment
        self.flushed = False

    async def get(self, model, primary_key):
        if model is DigitalWorkerRunRecord and primary_key == self.run.run_id:
            return self.run
        if (
            model is DigitalWorkerAssignmentRecord
            and primary_key == self.assignment.assignment_id
        ):
            return self.assignment
        return None

    async def flush(self) -> None:
        self.flushed = True
