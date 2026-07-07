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


@pytest.mark.asyncio
async def test_nominatim_client_parses_geocoding_response(monkeypatch) -> None:
    captured = {}

    async def fake_get_json(url, *, params=None, headers=None):
        captured.update({"url": url, "params": params, "headers": headers})
        return [
            {
                "display_name": "100 Main St, Austin, Texas",
                "lat": "30.1",
                "lon": "-97.1",
                "address": {"city": "Austin", "state": "Texas"},
            }
        ]

    monkeypatch.setattr(geocoding, "get_json", fake_get_json)

    result = await geocoding.NominatimClient(user_agent="Signal tests").geocode(
        street="100 Main St",
        city="Austin",
        state="TX",
        country="US",
    )

    assert captured["url"] == geocoding.NOMINATIM_SEARCH_URL
    assert captured["params"]["format"] == "jsonv2"
    assert captured["headers"]["User-Agent"] == "Signal tests"
    assert result is not None
    assert result.latitude == 30.1
    assert result.city == "Austin"


@pytest.mark.asyncio
async def test_census_client_parses_acs_place_response(monkeypatch) -> None:
    async def fake_get_json(url, *, params=None):
        assert url == census.CENSUS_ACS_PROFILE_URL
        assert params["for"] == "place:*"
        assert params["in"] == "state:48"
        return [
            ["NAME", "DP04_0046PE", "DP04_0134E", "DP02_0001E", "state", "place"],
            ["Austin city, Texas", "62.5", "1901", "500000", "48", "05000"],
        ]

    monkeypatch.setattr(census, "get_json", fake_get_json)

    result = await census.CensusAcsClient().market_snapshot(city="Austin", state="TX")

    assert result is not None
    assert result.renter_share == 0.625
    assert result.median_rent == 1901


@pytest.mark.asyncio
async def test_datausa_client_parses_state_household_growth(monkeypatch) -> None:
    async def fake_get_json(url, *, params=None):
        assert url == datausa.DATAUSA_API_URL
        assert params["Geography"] == "04000US48"
        return {"data": [{"Households": "110"}, {"Households": "100"}]}

    monkeypatch.setattr(datausa, "get_json", fake_get_json)

    result = await datausa.DataUsaClient().state_snapshot(state="TX")

    assert result is not None
    assert result.household_growth == 10


@pytest.mark.asyncio
async def test_fred_client_parses_rent_and_unemployment(monkeypatch) -> None:
    async def fake_get_json(url, *, params=None):
        assert url == fred.FRED_OBSERVATIONS_URL
        if params["series_id"] == fred.NATIONAL_RENT_SERIES_ID:
            values = list(range(100, 118))
        else:
            values = [3.4, 3.2]
        return {
            "observations": [
                {"date": f"2025-{index + 1:02d}-01", "value": str(value)}
                for index, value in enumerate(reversed(values))
            ]
        }

    monkeypatch.setattr(fred, "get_json", fake_get_json)

    result = await fred.FredClient(api_key="test").snapshot(state="TX")

    assert result is not None
    assert round(result.rent_growth_yoy or 0, 1) == 11.4
    assert result.unemployment_rate == 3.2


@pytest.mark.asyncio
async def test_news_client_parses_recent_trigger(monkeypatch) -> None:
    async def fake_get_json(url, *, params=None):
        assert url == news.NEWS_API_EVERYTHING_URL
        assert params["sortBy"] == "publishedAt"
        return {"articles": [{"title": "Regional expansion", "url": "https://example.test"}]}

    monkeypatch.setattr(news, "get_json", fake_get_json)

    result = await news.NewsApiClient(api_key="test").recent_trigger(
        company="Example Homes"
    )

    assert result is not None
    assert result.trigger == "Regional expansion"


@pytest.mark.asyncio
async def test_wikipedia_client_parses_company_snapshot(monkeypatch) -> None:
    async def fake_get_json(url, *, params=None, headers=None):
        assert url == wikipedia.WIKIPEDIA_SEARCH_URL
        assert params["limit"] == 1
        assert headers["User-Agent"] == "Signal tests"
        return {
            "pages": [
                {
                    "title": "Example Homes",
                    "excerpt": "Company background",
                }
            ]
        }

    monkeypatch.setattr(wikipedia, "get_json", fake_get_json)

    result = await wikipedia.WikipediaClient(
        user_agent="Signal tests"
    ).company_snapshot(company="Example Homes")

    assert result is not None
    assert result.summary == "Company background"
    assert result.url == "https://en.wikipedia.org/wiki/Example Homes"


@pytest.mark.asyncio
async def test_domain_mx_client_checks_domain(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.infrastructure.public_data.domain._has_mx_record",
        lambda domain: domain == "operator.example",
    )

    result = await DomainMxClient().domain_snapshot(email="rep@operator.example")

    assert result.has_mx is True
