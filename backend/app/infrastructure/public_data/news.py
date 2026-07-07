import httpx

from app.infrastructure.public_data.http import get_json
from app.infrastructure.public_data.types import NewsSnapshot

NEWS_API_EVERYTHING_URL = "https://newsapi.org/v2/everything"


class NewsApiClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        http_client: httpx.AsyncClient | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.api_key = api_key
        self.http_client = http_client
        self.transport = transport

    async def recent_trigger(self, *, company: str) -> NewsSnapshot | None:
        if not self.api_key:
            return None
        payload = await get_json(
            NEWS_API_EVERYTHING_URL,
            params={
                "q": f'"{company}"',
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 1,
                "apiKey": self.api_key,
            },
            client=self.http_client,
            transport=self.transport,
        )
        if not isinstance(payload, dict):
            return None
        articles = payload.get("articles")
        if not isinstance(articles, list) or not articles:
            return None
        first = articles[0]
        if not isinstance(first, dict):
            return None
        title = first.get("title")
        if not title:
            return None
        return NewsSnapshot(trigger=str(title), url=_string_or_none(first.get("url")))


def _string_or_none(value: object) -> str | None:
    return str(value) if value else None
