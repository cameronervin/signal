from typing import Any

import httpx

DEFAULT_TIMEOUT_SECONDS = 8.0


async def get_json(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    request_timeout: float = DEFAULT_TIMEOUT_SECONDS,
    client: httpx.AsyncClient | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> Any:
    if client is not None and transport is None:
        response = await client.get(
            url,
            params=params,
            headers=headers,
            timeout=request_timeout,
        )
        response.raise_for_status()
        return response.json()

    async with httpx.AsyncClient(
        timeout=request_timeout,
        follow_redirects=True,
        transport=transport,
    ) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
