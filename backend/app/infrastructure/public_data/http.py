from typing import Any

import httpx

DEFAULT_TIMEOUT_SECONDS = 8.0


async def get_json(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    request_timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> Any:
    async with httpx.AsyncClient(
        timeout=request_timeout,
        follow_redirects=True,
    ) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
