import pytest

from app.workers.tasks import _execute_signal_agent_run


@pytest.mark.asyncio
async def test_worker_execution_returns_json_safe_state() -> None:
    result = await _execute_signal_agent_run(
        {
            "lead_id": "lead_test",
            "run_id": "run_test",
            "lead": {
                "contact_name": "Sarah Chen",
                "email": "sarah@meridianresidential.example",
                "company": "Meridian Residential",
                "role": "VP Leasing",
                "property_address": "123 Market St",
                "city": "Austin",
                "state": "TX",
                "country": "US",
            },
            "activity_log": ["api_insert: lead received"],
        }
    )

    assert result["gates"]["status"] == "passed"
    assert result["score"]["tier"] == "A"
    assert result["draft"]["body"]
