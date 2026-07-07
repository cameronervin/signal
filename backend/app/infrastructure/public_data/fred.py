from typing import Any

import httpx

from app.infrastructure.public_data.http import get_json
from app.infrastructure.public_data.types import FredSnapshot

FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"
NATIONAL_RENT_SERIES_ID = "CUSR0000SEHA"


class FredClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.api_key = api_key
        self.transport = transport

    async def snapshot(self, *, state: str) -> FredSnapshot | None:
        if not self.api_key:
            return None
        rent_growth = await self._latest_yoy_percent(NATIONAL_RENT_SERIES_ID)
        unemployment = await self._latest_observation(f"{state.upper()}UR")
        if rent_growth is None and unemployment is None:
            return None
        return FredSnapshot(
            rent_growth_yoy=rent_growth,
            unemployment_rate=unemployment,
        )

    async def _latest_yoy_percent(self, series_id: str) -> float | None:
        observations = await self._observations(series_id, limit=18)
        values = [_number(row.get("value")) for row in observations]
        numeric = [value for value in values if value is not None]
        if len(numeric) < 13:
            return None
        current = numeric[-1]
        previous_year = numeric[-13]
        if previous_year == 0:
            return None
        return ((current - previous_year) / previous_year) * 100

    async def _latest_observation(self, series_id: str) -> float | None:
        observations = await self._observations(series_id, limit=6)
        for row in reversed(observations):
            value = _number(row.get("value"))
            if value is not None:
                return value
        return None

    async def _observations(
        self,
        series_id: str,
        *,
        limit: int,
    ) -> list[dict[str, Any]]:
        payload = await get_json(
            FRED_OBSERVATIONS_URL,
            params={
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": limit,
            },
            transport=self.transport,
        )
        if not isinstance(payload, dict):
            return []
        observations = payload.get("observations")
        if not isinstance(observations, list):
            return []
        return [row for row in reversed(observations) if isinstance(row, dict)]


def _number(value: object) -> float | None:
    try:
        parsed = float(str(value))
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None
