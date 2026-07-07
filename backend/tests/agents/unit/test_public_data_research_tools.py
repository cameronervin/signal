import json

import pytest

from app.agents.tools.public_data import (
    create_census_tool,
    create_datausa_tool,
    create_domain_tool,
    create_fred_tool,
    create_geocoding_tool,
    create_news_tool,
    create_wikipedia_tool,
)
from app.infrastructure.public_data.types import (
    CensusMarketSnapshot,
    CompanySnapshot,
    DataUsaSnapshot,
    DomainSnapshot,
    FredSnapshot,
    GeocodingResult,
    NewsSnapshot,
)


class FakeResearchPublicDataClient:
    async def geocode_address(self, **kwargs):
        return GeocodingResult(
            display_name="100 Main St, Austin, Texas",
            latitude=30.1,
            longitude=-97.1,
            city="Austin",
            state="Texas",
        )

    async def census_market_snapshot(self, **kwargs):
        return CensusMarketSnapshot(
            renter_share=0.64,
            median_rent=1925,
            household_count=500000,
        )

    async def datausa_state_snapshot(self, **kwargs):
        return DataUsaSnapshot(household_growth=3.2)

    async def fred_snapshot(self, **kwargs):
        return FredSnapshot(rent_growth_yoy=5.4, unemployment_rate=3.1)

    async def news_recent_trigger(self, **kwargs):
        return NewsSnapshot(
            trigger="Regional portfolio expansion",
            url="https://example.test",
        )

    async def wikipedia_company_snapshot(self, **kwargs):
        return CompanySnapshot(
            summary="Company background",
            url="https://example.test/wiki",
        )

    async def domain_snapshot_for_domain(self, **kwargs):
        return DomainSnapshot(has_mx=True)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_factory", "arguments", "expected_label"),
    [
        (
            create_geocoding_tool,
            {
                "street": "100 Main St",
                "city": "Austin",
                "state": "TX",
                "country": "US",
            },
            "Geocoded property",
        ),
        (
            create_census_tool,
            {"city": "Austin", "state": "TX"},
            "Renter share",
        ),
        (create_datausa_tool, {"state": "TX"}, "Household growth"),
        (create_fred_tool, {"state": "TX"}, "Rent growth"),
        (create_news_tool, {"company": "Example Homes"}, "Trigger event"),
        (
            create_wikipedia_tool,
            {"company": "Example Homes"},
            "Company background",
        ),
        (create_domain_tool, {"domain": "operator.example"}, "Corporate domain MX"),
    ],
)
async def test_public_data_research_tools_return_normalized_json(
    tool_factory,
    arguments,
    expected_label,
) -> None:
    tool = tool_factory()

    assert "public_data_client" not in tool.args
    result = await tool.ainvoke(
        {
            **arguments,
            "public_data_client": FakeResearchPublicDataClient(),
        }
    )
    payload = json.loads(result)

    assert payload["status"] == "ok"
    assert {fact["label"] for fact in payload["source_facts"]} >= {expected_label}


@pytest.mark.asyncio
async def test_public_data_research_tool_sanitizes_failures() -> None:
    class FailingClient:
        async def census_market_snapshot(self, **kwargs):
            raise RuntimeError("upstream leaked detail")

    result = await create_census_tool().ainvoke(
        {
            "city": "Austin",
            "state": "TX",
            "public_data_client": FailingClient(),
        }
    )
    payload = json.loads(result)

    assert payload["status"] == "unavailable"
    assert "upstream leaked detail" not in result
