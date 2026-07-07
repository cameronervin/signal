from dataclasses import dataclass
from time import monotonic
from typing import Any

from app.infrastructure.public_data.census import CensusAcsClient
from app.infrastructure.public_data.datausa import DataUsaClient
from app.infrastructure.public_data.domain import DomainMxClient
from app.infrastructure.public_data.fixtures import company_units_hint, demo_enrichment
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
    use_fixtures: bool = True
    news_api_key: str | None = None
    fred_api_key: str | None = None
    census_api_key: str | None = None
    user_agent: str = "Signal API local demo"
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
    ) -> None:
        self.config = config
        self.geocoding = geocoding or NominatimClient(
            user_agent=config.user_agent,
            email=config.nominatim_email,
        )
        self.census = census or CensusAcsClient(api_key=config.census_api_key)
        self.datausa = datausa or DataUsaClient()
        self.fred = fred or FredClient(api_key=config.fred_api_key)
        self.news = news or NewsApiClient(api_key=config.news_api_key)
        self.wikipedia = wikipedia or WikipediaClient(user_agent=config.user_agent)
        self.domain = domain or DomainMxClient()
        self._cache: dict[str, tuple[float, Enrichment]] = {}

    async def enrich(self, lead: LeadCreate) -> Enrichment:
        cache_key = lead.model_dump_json()
        cached = self._cache.get(cache_key)
        if cached and monotonic() - cached[0] < self.config.cache_ttl_seconds:
            return cached[1]

        if self.config.use_fixtures:
            enrichment = demo_enrichment(lead.company, lead.city, lead.state)
            self._cache[cache_key] = (monotonic(), enrichment)
            return enrichment

        fallback = demo_enrichment(lead.company, lead.city, lead.state)
        geocoding = await _attempt(
            self.geocoding.geocode(
                street=lead.property_address,
                city=lead.city,
                state=lead.state,
                country=lead.country,
            )
        )
        census = await _attempt(
            self.census.market_snapshot(city=lead.city, state=lead.state)
        )
        datausa = await _attempt(self.datausa.state_snapshot(state=lead.state))
        fred = await _attempt(self.fred.snapshot(state=lead.state))
        news = await _attempt(self.news.recent_trigger(company=lead.company))
        wikipedia = await _attempt(
            self.wikipedia.company_snapshot(company=lead.company)
        )
        domain = await _attempt(self.domain.domain_snapshot(email=str(lead.email)))

        enrichment = _merge_snapshots(
            fallback=fallback,
            company=lead.company,
            city=lead.city,
            state=lead.state,
            geocoding=geocoding,
            census=census,
            datausa=datausa,
            fred=fred,
            news=news,
            wikipedia=wikipedia,
            domain=domain,
        )
        self._cache[cache_key] = (monotonic(), enrichment)
        return enrichment


async def _attempt(awaitable: Any) -> Any:
    try:
        return await awaitable
    except Exception:  # noqa: BLE001
        return None


def _merge_snapshots(
    *,
    fallback: Enrichment,
    company: str,
    city: str,
    state: str,
    geocoding: GeocodingResult | None,
    census: CensusMarketSnapshot | None,
    datausa: DataUsaSnapshot | None,
    fred: FredSnapshot | None,
    news: NewsSnapshot | None,
    wikipedia: CompanySnapshot | None,
    domain: DomainSnapshot | None,
) -> Enrichment:
    market = _market_label(city, state, geocoding)
    renter_share = _first_not_none(
        census.renter_share if census else None,
        fallback.renter_share,
    )
    median_rent = _first_not_none(
        census.median_rent if census else None,
        fallback.median_rent,
    )
    rent_growth = _first_not_none(
        fred.rent_growth_yoy if fred else None,
        fallback.rent_growth_yoy,
    )
    household_growth = _first_not_none(
        datausa.household_growth if datausa else None,
        fallback.household_growth,
    )
    unemployment = _first_not_none(
        fred.unemployment_rate if fred else None,
        fallback.unemployment_rate,
    )
    recent_trigger = _first_not_none(
        news.trigger if news else None,
        fallback.recent_trigger,
    )
    sources = _source_facts(
        renter_share=renter_share,
        median_rent=median_rent,
        rent_growth=rent_growth,
        household_growth=household_growth,
        unemployment=unemployment,
        recent_trigger=recent_trigger,
        news=news,
        wikipedia=wikipedia,
        domain=domain,
    )
    return Enrichment(
        market=market,
        coordinates=(
            (geocoding.latitude, geocoding.longitude)
            if geocoding is not None
            else fallback.coordinates
        ),
        renter_share=renter_share,
        median_rent=median_rent,
        rent_growth_yoy=rent_growth,
        household_growth=household_growth,
        unemployment_rate=unemployment,
        company_units=company_units_hint(company),
        recent_trigger=recent_trigger,
        sources=sources or fallback.sources,
    )


def _market_label(
    city: str,
    state: str,
    geocoding: GeocodingResult | None,
) -> str:
    if geocoding is not None and geocoding.city and geocoding.state:
        return f"{geocoding.city}, {geocoding.state}"
    return f"{city}, {state}"


def _first_not_none[T](primary: T | None, fallback: T | None) -> T | None:
    return primary if primary is not None else fallback


def _source_facts(
    *,
    renter_share: float | None,
    median_rent: int | None,
    rent_growth: float | None,
    household_growth: float | None,
    unemployment: float | None,
    recent_trigger: str | None,
    news: NewsSnapshot | None,
    wikipedia: CompanySnapshot | None,
    domain: DomainSnapshot | None,
) -> list[SourceFact]:
    facts: list[SourceFact] = []
    if renter_share is not None:
        facts.append(
            SourceFact(
                source="Census ACS",
                label="Renter share",
                value=f"{renter_share:.0%}",
            )
        )
    if median_rent is not None:
        facts.append(
            SourceFact(
                source="Census ACS",
                label="Median rent",
                value=f"${median_rent:,}",
            )
        )
    if rent_growth is not None:
        facts.append(
            SourceFact(
                source="FRED",
                label="Rent growth",
                value=f"{rent_growth:.1f}% YoY",
            )
        )
    if household_growth is not None:
        facts.append(
            SourceFact(
                source="DataUSA",
                label="Household growth",
                value=f"{household_growth:.1f}% YoY",
            )
        )
    if unemployment is not None:
        facts.append(
            SourceFact(
                source="FRED",
                label="Unemployment rate",
                value=f"{unemployment:.1f}%",
            )
        )
    if recent_trigger is not None:
        facts.append(
            SourceFact(
                source=news.source_name if news else "News",
                label="Trigger event",
                value=recent_trigger,
                url=news.url if news else None,
            )
        )
    if wikipedia and wikipedia.summary:
        facts.append(
            SourceFact(
                source=wikipedia.source_name,
                label="Company background",
                value=wikipedia.summary,
                url=wikipedia.url,
            )
        )
    if domain and domain.has_mx is not None:
        facts.append(
            SourceFact(
                source=domain.source_name,
                label="Corporate domain MX",
                value="MX records found" if domain.has_mx else "No MX records found",
            )
        )
    return facts
