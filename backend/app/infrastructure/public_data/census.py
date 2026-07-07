from typing import Any

from app.infrastructure.public_data.http import get_json
from app.infrastructure.public_data.state_fips import STATE_FIPS
from app.infrastructure.public_data.types import CensusMarketSnapshot

CENSUS_ACS_PROFILE_URL = "https://api.census.gov/data/2024/acs/acs5/profile"
CENSUS_VARIABLES = "NAME,DP04_0046PE,DP04_0134E,DP02_0001E"


class CensusAcsClient:
    def __init__(self, *, api_key: str | None = None) -> None:
        self.api_key = api_key

    async def market_snapshot(
        self,
        *,
        city: str,
        state: str,
    ) -> CensusMarketSnapshot | None:
        state_fips = STATE_FIPS.get(state.upper())
        if state_fips is None:
            return None
        params: dict[str, Any] = {
            "get": CENSUS_VARIABLES,
            "for": "place:*",
            "in": f"state:{state_fips}",
        }
        if self.api_key:
            params["key"] = self.api_key
        payload = await get_json(CENSUS_ACS_PROFILE_URL, params=params)
        if not isinstance(payload, list) or len(payload) < 2:
            return None
        headers = [str(header) for header in payload[0]]
        rows = payload[1:]
        city_normalized = city.lower()
        selected = next(
            (
                row
                for row in rows
                if row
                and city_normalized in str(row[0]).lower()
            ),
            None,
        )
        if selected is None:
            return None
        row_data = dict(zip(headers, selected, strict=False))
        return CensusMarketSnapshot(
            renter_share=_optional_percent(row_data.get("DP04_0046PE")),
            median_rent=_optional_int(row_data.get("DP04_0134E")),
            household_count=_optional_int(row_data.get("DP02_0001E")),
        )


def _optional_percent(value: object) -> float | None:
    parsed = _optional_float(value)
    if parsed is None:
        return None
    return parsed / 100


def _optional_float(value: object) -> float | None:
    try:
        parsed = float(str(value))
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def _optional_int(value: object) -> int | None:
    parsed = _optional_float(value)
    if parsed is None:
        return None
    return int(parsed)
