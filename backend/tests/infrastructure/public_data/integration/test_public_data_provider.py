import pytest

from app.infrastructure.public_data.provider import (
    PublicDataClient,
    PublicDataClientConfig,
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
from app.schemas.lead import LeadCreate


class FakeGeocoding:
    async def geocode(self, **kwargs):
        return GeocodingResult(
            display_name="100 Main St",
            latitude=30.0,
            longitude=-97.0,
            city="Austin",
            state="Texas",
        )


class FakeCensus:
    async def market_snapshot(self, **kwargs):
        return CensusMarketSnapshot(renter_share=0.64, median_rent=1925)


class FakeDataUsa:
    async def state_snapshot(self, **kwargs):
        return DataUsaSnapshot(household_growth=3.2)


class FakeFred:
    async def snapshot(self, **kwargs):
        return FredSnapshot(rent_growth_yoy=5.4, unemployment_rate=3.1)


class FakeNews:
    async def recent_trigger(self, **kwargs):
        return NewsSnapshot(trigger="Regional portfolio expansion", url="https://example.test")


class FakeWikipedia:
    async def company_snapshot(self, **kwargs):
        return CompanySnapshot(summary="Company background", url="https://example.test/wiki")


class FakeDomain:
    async def domain_snapshot(self, **kwargs):
        return DomainSnapshot(has_mx=True)


@pytest.mark.asyncio
async def test_public_data_client_merges_live_adapter_snapshots() -> None:
    client = PublicDataClient(
        PublicDataClientConfig(use_fixtures=False),
        geocoding=FakeGeocoding(),
        census=FakeCensus(),
        datausa=FakeDataUsa(),
        fred=FakeFred(),
        news=FakeNews(),
        wikipedia=FakeWikipedia(),
        domain=FakeDomain(),
    )
    lead = LeadCreate(
        contact_name="Sarah Chen",
        email="sarah@meridianresidential.example",
        company="Meridian Residential",
        role="VP Leasing",
        property_address="123 Market St",
        city="Austin",
        state="TX",
        country="US",
    )

    enrichment = await client.enrich(lead)

    assert enrichment.market == "Austin, Texas"
    assert enrichment.coordinates == (30.0, -97.0)
    assert enrichment.renter_share == 0.64
    assert enrichment.rent_growth_yoy == 5.4
    assert enrichment.recent_trigger == "Regional portfolio expansion"
    assert {source.source for source in enrichment.sources} >= {
        "Census ACS",
        "DataUSA",
        "FRED",
        "News API",
        "Wikipedia",
        "DNS MX",
    }
