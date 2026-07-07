from typing import Any

from app.infrastructure.public_data.http import get_json
from app.infrastructure.public_data.state_fips import STATE_FIPS
from app.infrastructure.public_data.types import DataUsaSnapshot

DATAUSA_API_URL = "https://datausa.io/api/data"


class DataUsaClient:
    async def state_snapshot(self, *, state: str) -> DataUsaSnapshot | None:
        state_fips = STATE_FIPS.get(state.upper())
        if state_fips is None:
            return None
        payload = await get_json(
            DATAUSA_API_URL,
            params={
                "Geography": f"04000US{state_fips}",
                "measure": "Households",
                "year": "latest",
            },
        )
        if not isinstance(payload, dict):
            return None
        rows = payload.get("data")
        if not isinstance(rows, list) or not rows:
            return None
        latest = _first_numeric(rows, "Households")
        previous_rows = [row for row in rows if isinstance(row, dict)]
        if latest is None or len(previous_rows) < 2:
            return DataUsaSnapshot()
        previous = _number(previous_rows[1].get("Households"))
        if previous in (None, 0):
            return DataUsaSnapshot()
        return DataUsaSnapshot(household_growth=((latest - previous) / previous) * 100)


def _first_numeric(rows: list[Any], key: str) -> float | None:
    for row in rows:
        if isinstance(row, dict):
            value = _number(row.get(key))
            if value is not None:
                return value
    return None


def _number(value: object) -> float | None:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None
