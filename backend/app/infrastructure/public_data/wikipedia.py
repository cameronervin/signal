import httpx

from app.infrastructure.public_data.http import get_json
from app.infrastructure.public_data.types import CompanySnapshot

WIKIPEDIA_SEARCH_URL = "https://en.wikipedia.org/w/rest.php/v1/search/page"


class WikipediaClient:
    def __init__(
        self,
        *,
        user_agent: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.user_agent = user_agent
        self.transport = transport

    async def company_snapshot(self, *, company: str) -> CompanySnapshot | None:
        payload = await get_json(
            WIKIPEDIA_SEARCH_URL,
            params={"q": company, "limit": 1},
            headers={"User-Agent": self.user_agent},
            transport=self.transport,
        )
        if not isinstance(payload, dict):
            return None
        pages = payload.get("pages")
        if not isinstance(pages, list) or not pages:
            return None
        first = pages[0]
        if not isinstance(first, dict):
            return None
        summary = first.get("excerpt") or first.get("description")
        title = first.get("title")
        return CompanySnapshot(
            summary=str(summary) if summary else None,
            url=f"https://en.wikipedia.org/wiki/{title}" if title else None,
        )
