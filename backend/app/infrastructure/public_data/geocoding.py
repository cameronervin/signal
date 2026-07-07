from typing import Any

import httpx

from app.infrastructure.public_data.http import get_json
from app.infrastructure.public_data.types import GeocodingResult

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"


class NominatimClient:
    def __init__(
        self,
        *,
        user_agent: str,
        email: str | None = None,
        http_client: httpx.AsyncClient | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.user_agent = user_agent
        self.email = email
        self.http_client = http_client
        self.transport = transport

    async def geocode(
        self,
        *,
        street: str,
        city: str,
        state: str,
        country: str,
    ) -> GeocodingResult | None:
        params: dict[str, Any] = {
            "street": street,
            "city": city,
            "state": state,
            "country": country,
            "format": "jsonv2",
            "addressdetails": 1,
            "limit": 1,
            "countrycodes": "us",
        }
        if self.email:
            params["email"] = self.email
        payload = await get_json(
            NOMINATIM_SEARCH_URL,
            params=params,
            headers={"User-Agent": self.user_agent},
            client=self.http_client,
            transport=self.transport,
        )
        if not isinstance(payload, list) or not payload:
            return None
        first = payload[0]
        address = first.get("address", {})
        return GeocodingResult(
            display_name=str(first.get("display_name", "")),
            latitude=float(first["lat"]),
            longitude=float(first["lon"]),
            city=address.get("city") or address.get("town") or address.get("village"),
            state=address.get("state"),
        )
