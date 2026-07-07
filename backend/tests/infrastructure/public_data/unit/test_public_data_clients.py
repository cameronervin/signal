import httpx
import pytest

from app.infrastructure.public_data import (
    census,
    datausa,
    fred,
    geocoding,
    news,
    wikipedia,
)
from app.infrastructure.public_data.domain import DomainMxClient
from app.infrastructure.public_data.http import get_json


@pytest.mark.asyncio
async def test_get_json_uses_transport_params_headers_and_status_errors() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/error":
            return httpx.Response(503, json={"error": "unavailable"})
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)

    payload = await get_json(
        "https://api.example.test/search",
        params={"q": "Austin"},
        headers={"User-Agent": "Signal tests"},
        transport=transport,
    )

    assert payload == {"ok": True}
    assert requests[0].url == "https://api.example.test/search?q=Austin"
    assert requests[0].headers["user-agent"] == "Signal tests"
    with pytest.raises(httpx.HTTPStatusError):
        await get_json("https://api.example.test/error", transport=transport)


@pytest.mark.asyncio
async def test_get_json_can_use_shared_async_client() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        follow_redirects=True,
    ) as shared_client:
        payload = await get_json(
            "https://api.example.test/search",
            params={"q": "Austin"},
            headers={"User-Agent": "Signal tests"},
            client=shared_client,
        )

    assert payload == {"ok": True}
    assert requests[0].url == "https://api.example.test/search?q=Austin"
    assert requests[0].headers["user-agent"] == "Signal tests"


@pytest.mark.asyncio
async def test_get_json_prefers_explicit_transport_over_shared_client() -> None:
    shared_requests: list[httpx.Request] = []
    explicit_requests: list[httpx.Request] = []

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(
            lambda request: (
                shared_requests.append(request)
                or httpx.Response(200, json={"source": "shared"})
            )
        ),
    ) as shared_client:
        payload = await get_json(
            "https://api.example.test/search",
            client=shared_client,
            transport=httpx.MockTransport(
                lambda request: (
                    explicit_requests.append(request)
                    or httpx.Response(200, json={"source": "explicit"})
                )
            ),
        )

    assert payload == {"source": "explicit"}
    assert explicit_requests
    assert shared_requests == []


@pytest.mark.asyncio
async def test_nominatim_client_sends_search_contract() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json=[
                {
                    "display_name": "100 Main St, Austin, Texas",
                    "lat": "30.1",
                    "lon": "-97.1",
                    "address": {"city": "Austin", "state": "Texas"},
                }
            ],
        )

    result = await geocoding.NominatimClient(
        user_agent="Signal tests",
        email="ops@example.test",
        transport=httpx.MockTransport(handler),
    ).geocode(
        street="100 Main St",
        city="Austin",
        state="TX",
        country="US",
    )

    assert captured[0].url.host == "nominatim.openstreetmap.org"
    assert captured[0].url.params["street"] == "100 Main St"
    assert captured[0].url.params["format"] == "jsonv2"
    assert captured[0].url.params["email"] == "ops@example.test"
    assert captured[0].headers["user-agent"] == "Signal tests"
    assert result is not None
    assert result.latitude == 30.1
    assert result.city == "Austin"


@pytest.mark.asyncio
async def test_nominatim_client_returns_none_for_malformed_payload() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={}))

    result = await geocoding.NominatimClient(
        user_agent="Signal tests",
        transport=transport,
    ).geocode(
        street="100 Main St",
        city="Austin",
        state="TX",
        country="US",
    )

    assert result is None


@pytest.mark.asyncio
async def test_census_client_sends_acs_place_contract() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json=[
                ["NAME", "DP04_0046PE", "DP04_0134E", "DP02_0001E", "state", "place"],
                ["Austin city, Texas", "62.5", "1901", "500000", "48", "05000"],
            ],
        )

    result = await census.CensusAcsClient(
        api_key="census-key",
        transport=httpx.MockTransport(handler),
    ).market_snapshot(city="Austin", state="TX")

    assert str(captured[0].url.copy_with(query=None)) == census.CENSUS_ACS_PROFILE_URL
    assert captured[0].url.params["for"] == "place:*"
    assert captured[0].url.params["in"] == "state:48"
    assert captured[0].url.params["key"] == "census-key"
    assert result is not None
    assert result.renter_share == 0.625
    assert result.median_rent == 1901


@pytest.mark.asyncio
async def test_census_client_returns_none_for_empty_rows() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=[]))

    result = await census.CensusAcsClient(
        transport=transport,
    ).market_snapshot(city="Austin", state="TX")

    assert result is None


@pytest.mark.asyncio
async def test_datausa_client_sends_household_growth_contract() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={"data": [{"Households": "110"}, {"Households": "100"}]},
        )

    result = await datausa.DataUsaClient(
        transport=httpx.MockTransport(handler),
    ).state_snapshot(state="TX")

    assert str(captured[0].url.copy_with(query=None)) == datausa.DATAUSA_API_URL
    assert captured[0].url.params["Geography"] == "04000US48"
    assert captured[0].url.params["measure"] == "Households"
    assert result is not None
    assert result.household_growth == 10


@pytest.mark.asyncio
async def test_fred_client_sends_rent_and_unemployment_contract() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        if request.url.params["series_id"] == fred.NATIONAL_RENT_SERIES_ID:
            values = list(range(100, 118))
        else:
            values = [3.4, 3.2]
        return httpx.Response(
            200,
            json={
                "observations": [
                    {"date": f"2025-{index + 1:02d}-01", "value": str(value)}
                    for index, value in enumerate(reversed(values))
                ]
            },
        )

    result = await fred.FredClient(
        api_key="fred-key",
        transport=httpx.MockTransport(handler),
    ).snapshot(state="TX")

    assert {request.url.params["series_id"] for request in captured} == {
        fred.NATIONAL_RENT_SERIES_ID,
        "TXUR",
    }
    assert all(request.url.params["api_key"] == "fred-key" for request in captured)
    assert result is not None
    assert round(result.rent_growth_yoy or 0, 1) == 11.4
    assert result.unemployment_rate == 3.2


@pytest.mark.asyncio
async def test_fred_client_without_key_does_not_request() -> None:
    called = False

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(200, json={})

    result = await fred.FredClient(
        transport=httpx.MockTransport(handler),
    ).snapshot(state="TX")

    assert result is None
    assert called is False


@pytest.mark.asyncio
async def test_news_client_sends_everything_contract() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={"articles": [{"title": "Regional expansion", "url": "https://example.test"}]},
        )

    result = await news.NewsApiClient(
        api_key="news-key",
        transport=httpx.MockTransport(handler),
    ).recent_trigger(company="Example Homes")

    assert str(captured[0].url.copy_with(query=None)) == news.NEWS_API_EVERYTHING_URL
    assert captured[0].url.params["q"] == '"Example Homes"'
    assert captured[0].url.params["sortBy"] == "publishedAt"
    assert captured[0].url.params["apiKey"] == "news-key"
    assert result is not None
    assert result.trigger == "Regional expansion"


@pytest.mark.asyncio
async def test_news_client_without_key_does_not_request() -> None:
    called = False

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(200, json={})

    result = await news.NewsApiClient(
        transport=httpx.MockTransport(handler),
    ).recent_trigger(company="Example Homes")

    assert result is None
    assert called is False


@pytest.mark.asyncio
async def test_wikipedia_client_sends_search_contract() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={
                "pages": [
                    {
                        "title": "Example Homes",
                        "excerpt": "Company background",
                    }
                ]
            },
        )

    result = await wikipedia.WikipediaClient(
        user_agent="Signal tests",
        transport=httpx.MockTransport(handler),
    ).company_snapshot(company="Example Homes")

    assert str(captured[0].url.copy_with(query=None)) == wikipedia.WIKIPEDIA_SEARCH_URL
    assert captured[0].url.params["q"] == "Example Homes"
    assert captured[0].url.params["limit"] == "1"
    assert captured[0].headers["user-agent"] == "Signal tests"
    assert result is not None
    assert result.summary == "Company background"
    assert result.url == "https://en.wikipedia.org/wiki/Example Homes"


@pytest.mark.asyncio
async def test_domain_mx_client_checks_domain(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.infrastructure.public_data.domain._has_mx_record",
        lambda domain: domain == "operator.example",
    )

    result = await DomainMxClient().domain_snapshot(email="rep@operator.example")

    assert result.has_mx is True
