from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from time import monotonic
from typing import Any

import httpx

from app.infrastructure.public_data.census import CensusAcsClient
from app.infrastructure.public_data.datausa import DataUsaClient
from app.infrastructure.public_data.domain import DomainMxClient
from app.infrastructure.public_data.fixtures import company_units_hint
from app.infrastructure.public_data.fred import FredClient
from app.infrastructure.public_data.geocoding import NominatimClient
from app.infrastructure.public_data.news import NewsApiClient
from app.infrastructure.public_data.types import (
    CensusMarketSnapshot,
    CompanySnapshot,
    DataUsaSnapshot,
    DomainSnapshot,
    FredSnapshot,
    GeocodingResult,
    NewsSnapshot,
)
from app.infrastructure.public_data.wikipedia import WikipediaClient
from app.schemas.lead import Enrichment, LeadCreate, SourceFact


@dataclass(frozen=True)
class PublicDataClientConfig:
    news_api_key: str | None = None
    fred_api_key: str | None = None
    census_api_key: str | None = None
    user_agent: str = "Signal API"
    nominatim_email: str | None = None
    cache_ttl_seconds: int = 3600


class PublicDataClient:
    def __init__(
        self,
        config: PublicDataClientConfig,
        *,
        geocoding: NominatimClient | None = None,
        census: CensusAcsClient | None = None,
        datausa: DataUsaClient | None = None,
        fred: FredClient | None = None,
        news: NewsApiClient | None = None,
        wikipedia: WikipediaClient | None = None,
        domain: DomainMxClient | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.config = config
        self.http_client = http_client
        self.geocoding = geocoding or NominatimClient(
            user_agent=config.user_agent,
            email=config.nominatim_email,
            http_client=http_client,
        )
        self.census = census or CensusAcsClient(
            api_key=config.census_api_key,
            http_client=http_client,
        )
        self.datausa = datausa or DataUsaClient(http_client=http_client)
        self.fred = fred or FredClient(
            api_key=config.fred_api_key,
            http_client=http_client,
        )
        self.news = news or NewsApiClient(
            api_key=config.news_api_key,
            http_client=http_client,
        )
        self.wikipedia = wikipedia or WikipediaClient(
            user_agent=config.user_agent,
            http_client=http_client,
        )
        self.domain = domain or DomainMxClient()
        self._cache: dict[str, tuple[float, Any]] = {}

    async def enrich(self, lead: LeadCreate) -> Enrichment:
        cache_key = f"enrich:{lead.model_dump_json()}"
        cached = self._get_cached(cache_key)
        if isinstance(cached, Enrichment):
            return cached

        provider_warnings: list[str] = []
        geocoding = await _attempt(
            provider_warnings,
            "geocoding unavailable",
            self.geocode_address(
                street=lead.property_address,
                city=lead.city,
                state=lead.state,
                country=lead.country,
            )
        )
        census = await _attempt(
            provider_warnings,
            "market demographics unavailable",
            self.census_market_snapshot(city=lead.city, state=lead.state)
        )
        datausa = await _attempt(
            provider_warnings,
            "household growth data unavailable",
            self.datausa_state_snapshot(state=lead.state),
        )
        fred = await _attempt(
            provider_warnings,
            "economic data unavailable",
            self.fred_snapshot(state=lead.state),
        )
        news = await _attempt(
            provider_warnings,
            "company trigger data unavailable",
            self.news_recent_trigger(company=lead.company),
        )
        wikipedia = await _attempt(
            provider_warnings,
            "company background unavailable",
            self.wikipedia_company_snapshot(company=lead.company)
        )
        domain = await _attempt(
            provider_warnings,
            "domain validation unavailable",
            self.domain_snapshot(email=str(lead.email)),
        )

        enrichment = _merge_snapshots(
            company=lead.company,
            city=lead.city,
            state=lead.state,
            provider_warnings=provider_warnings,
            geocoding=geocoding,
            census=census,
            datausa=datausa,
            fred=fred,
            news=news,
            wikipedia=wikipedia,
            domain=domain,
        )
        self._set_cached(cache_key, enrichment)
        return enrichment

    async def geocode_address(
        self,
        *,
        street: str,
        city: str,
        state: str,
        country: str,
    ) -> GeocodingResult | None:
        return await self._cached_lookup(
            f"geocode:{street}:{city}:{state}:{country}",
            lambda: self.geocoding.geocode(
                street=street,
                city=city,
                state=state,
                country=country,
            ),
        )

    async def census_market_snapshot(
        self,
        *,
        city: str,
        state: str,
    ) -> CensusMarketSnapshot | None:
        return await self._cached_lookup(
            f"census:{city}:{state}",
            lambda: self.census.market_snapshot(city=city, state=state),
        )

    async def datausa_state_snapshot(self, *, state: str) -> DataUsaSnapshot | None:
        return await self._cached_lookup(
            f"datausa:{state}",
            lambda: self.datausa.state_snapshot(state=state),
        )

    async def fred_snapshot(self, *, state: str) -> FredSnapshot | None:
        return await self._cached_lookup(
            f"fred:{state}",
            lambda: self.fred.snapshot(state=state),
        )

    async def news_recent_trigger(self, *, company: str) -> NewsSnapshot | None:
        return await self._cached_lookup(
            f"news:{company}",
            lambda: self.news.recent_trigger(company=company),
        )

    async def wikipedia_company_snapshot(
        self,
        *,
        company: str,
    ) -> CompanySnapshot | None:
        return await self._cached_lookup(
            f"wikipedia:{company}",
            lambda: self.wikipedia.company_snapshot(company=company),
        )

    async def domain_snapshot(self, *, email: str) -> DomainSnapshot:
        domain = email.split("@")[-1].lower()
        return await self._cached_lookup(
            f"domain:{domain}",
            lambda: self.domain.domain_snapshot(email=email),
        )

    async def domain_snapshot_for_domain(self, *, domain: str) -> DomainSnapshot:
        normalized = domain.split("@")[-1].lower()
        return await self.domain_snapshot(email=f"contact@{normalized}")

    async def _cached_lookup[T](
        self,
        cache_key: str,
        factory: Callable[[], Awaitable[T]],
    ) -> T:
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        value = await factory()
        self._set_cached(cache_key, value)
        return value

    def _get_cached(self, cache_key: str) -> Any | None:
        cached = self._cache.get(cache_key)
        if cached and monotonic() - cached[0] < self.config.cache_ttl_seconds:
            return cached[1]
        return None

    def _set_cached(self, cache_key: str, value: Any) -> None:
        self._cache[cache_key] = (monotonic(), value)


async def _attempt(
    provider_warnings: list[str],
    warning: str,
    awaitable: Any,
) -> Any:
    try:
        return await awaitable
    except Exception:  # noqa: BLE001
        provider_warnings.append(warning)
        return None


def _merge_snapshots(
    *,
    company: str,
    city: str,
    state: str,
    provider_warnings: list[str],
    geocoding: GeocodingResult | None,
    census: CensusMarketSnapshot | None,
    datausa: DataUsaSnapshot | None,
    fred: FredSnapshot | None,
    news: NewsSnapshot | None,
    wikipedia: CompanySnapshot | None,
    domain: DomainSnapshot | None,
) -> Enrichment:
    market = _market_label(city, state, geocoding)
    renter_share = census.renter_share if census else None
    median_rent = census.median_rent if census else None
    rent_growth = fred.rent_growth_yoy if fred else None
    household_growth = datausa.household_growth if datausa else None
    unemployment = fred.unemployment_rate if fred else None
    recent_trigger = news.trigger if news else None
    sources = [
        *source_facts_for_census(census),
        *source_facts_for_fred(fred),
        *source_facts_for_datausa(datausa),
        *source_facts_for_news(news),
        *source_facts_for_wikipedia(wikipedia),
        *source_facts_for_domain(domain),
    ]
    return Enrichment(
        market=market,
        coordinates=(
            (geocoding.latitude, geocoding.longitude)
            if geocoding is not None
            else None
        ),
        renter_share=renter_share,
        median_rent=median_rent,
        rent_growth_yoy=rent_growth,
        household_growth=household_growth,
        unemployment_rate=unemployment,
        company_units=company_units_hint(company),
        recent_trigger=recent_trigger,
        sources=sources,
        provider_warnings=provider_warnings,
    )


def _market_label(
    city: str,
    state: str,
    geocoding: GeocodingResult | None,
) -> str:
    if geocoding is not None and geocoding.city and geocoding.state:
        return f"{geocoding.city}, {geocoding.state}"
    return f"{city}, {state}"


def source_facts_for_geocoding(
    geocoding: GeocodingResult | None,
) -> list[SourceFact]:
    if geocoding is None:
        return []
    return [
        SourceFact(
            source="OpenStreetMap Nominatim",
            label="Geocoded property",
            value=geocoding.display_name,
        )
    ]


def source_facts_for_census(
    census: CensusMarketSnapshot | None,
) -> list[SourceFact]:
    facts: list[SourceFact] = []
    if census is None:
        return facts
    if census.renter_share is not None:
        facts.append(
            SourceFact(
                source=census.source_name,
                label="Renter share",
                value=f"{census.renter_share:.0%}",
            )
        )
    if census.median_rent is not None:
        facts.append(
            SourceFact(
                source=census.source_name,
                label="Median rent",
                value=f"${census.median_rent:,}",
            )
        )
    if census.household_count is not None:
        facts.append(
            SourceFact(
                source=census.source_name,
                label="Household count",
                value=f"{census.household_count:,}",
            )
        )
    return facts


def source_facts_for_fred(fred: FredSnapshot | None) -> list[SourceFact]:
    facts: list[SourceFact] = []
    if fred is None:
        return facts
    if fred.rent_growth_yoy is not None:
        facts.append(
            SourceFact(
                source=fred.source_name,
                label="Rent growth",
                value=f"{fred.rent_growth_yoy:.1f}% YoY",
            )
        )
    if fred.unemployment_rate is not None:
        facts.append(
            SourceFact(
                source=fred.source_name,
                label="Unemployment rate",
                value=f"{fred.unemployment_rate:.1f}%",
            )
        )
    return facts


def source_facts_for_datausa(datausa: DataUsaSnapshot | None) -> list[SourceFact]:
    if datausa is None or datausa.household_growth is None:
        return []
    return [
        SourceFact(
            source=datausa.source_name,
            label="Household growth",
            value=f"{datausa.household_growth:.1f}% YoY",
        )
    ]


def source_facts_for_news(news: NewsSnapshot | None) -> list[SourceFact]:
    if news is None or news.trigger is None:
        return []
    return [
        SourceFact(
            source=news.source_name,
            label="Trigger event",
            value=news.trigger,
            url=news.url,
        )
    ]


def source_facts_for_wikipedia(
    wikipedia: CompanySnapshot | None,
) -> list[SourceFact]:
    if wikipedia is None or not wikipedia.summary:
        return []
    return [
        SourceFact(
            source=wikipedia.source_name,
            label="Company background",
            value=wikipedia.summary,
            url=wikipedia.url,
        )
    ]


def source_facts_for_domain(domain: DomainSnapshot | None) -> list[SourceFact]:
    if domain is None or domain.has_mx is None:
        return []
    return [
        SourceFact(
            source=domain.source_name,
            label="Corporate domain MX",
            value="MX records found" if domain.has_mx else "No MX records found",
        )
    ]
