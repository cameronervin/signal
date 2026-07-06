from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Literal

import dns.asyncresolver
import dns.exception
import dns.resolver
import httpx
from pydantic import BaseModel, Field, SecretStr

from app.schemas.lead import Enrichment, LeadCreate, SourceFact

ProviderCategory = Literal[
    "geocoding",
    "demographics",
    "economics",
    "local_context",
    "news_events",
    "company_context",
    "domain_quality",
    "llm",
]
ProviderWarningCode = Literal[
    "missing_key",
    "timeout",
    "schema_changed",
    "rate_limited",
    "provider_error",
    "fixture_selected",
    "fixture_unavailable",
]
RefreshPolicy = Literal["ttl", "refresh_after", "manual"]
PublicDataScalar = str | int | float | bool | None
PublicDataValue = PublicDataScalar | list[PublicDataScalar]

_WHITESPACE_RE = re.compile(r"\s+")

SANITIZED_WARNING_MESSAGES: dict[ProviderWarningCode, str] = {
    "missing_key": "Provider configuration is unavailable.",
    "timeout": "Provider request timed out.",
    "schema_changed": "Provider response shape changed.",
    "rate_limited": "Provider rate limit was reached.",
    "provider_error": "Provider request failed.",
    "fixture_selected": "Fixture data was selected.",
    "fixture_unavailable": "Fixture data is unavailable.",
}


def utc_now() -> datetime:
    return datetime.now(UTC)


def normalize_lookup_key(value: str) -> str:
    normalized = _WHITESPACE_RE.sub(" ", value.strip().lower())
    if "@" not in normalized:
        return normalized
    domain = normalized.rsplit("@", maxsplit=1)[-1]
    return f"email-domain:{domain}"


def normalize_provider_source(value: str) -> str:
    return _WHITESPACE_RE.sub(" ", value.strip().lower())


def _secret_is_configured(value: SecretStr | str | None) -> bool:
    if value is None:
        return False
    if isinstance(value, SecretStr):
        return bool(value.get_secret_value().strip())
    return bool(value.strip())


class ProviderWarning(BaseModel):
    provider_category: ProviderCategory
    code: ProviderWarningCode
    message: str
    retryable: bool = False

    @classmethod
    def from_code(
        cls,
        provider_category: ProviderCategory,
        code: ProviderWarningCode,
        *,
        retryable: bool = False,
    ) -> ProviderWarning:
        return cls(
            provider_category=provider_category,
            code=code,
            message=SANITIZED_WARNING_MESSAGES[code],
            retryable=retryable,
        )


class NormalizedPublicDataResult(BaseModel):
    provider_category: ProviderCategory
    lookup_key: str
    source: str
    data: dict[str, PublicDataValue] = Field(default_factory=dict)
    facts: list[SourceFact] = Field(default_factory=list)
    retrieved_at: datetime = Field(default_factory=utc_now)
    warnings: list[ProviderWarning] = Field(default_factory=list)
    is_fixture: bool = False
    cache_hit: bool = False

    def with_warning(self, warning: ProviderWarning) -> NormalizedPublicDataResult:
        return self.model_copy(update={"warnings": [*self.warnings, warning]})


class PublicDataCacheRecord(BaseModel):
    provider_category: ProviderCategory
    source: str
    lookup_key: str
    response: NormalizedPublicDataResult
    retrieved_at: datetime = Field(default_factory=utc_now)
    expires_at: datetime | None = None
    refresh_policy: RefreshPolicy = "ttl"

    def is_expired(self, now: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        return (now or utc_now()) >= self.expires_at


class InMemoryPublicDataCache:
    def __init__(self) -> None:
        self._records: dict[
            tuple[ProviderCategory, str, str], PublicDataCacheRecord
        ] = {}

    def get(
        self,
        provider_category: ProviderCategory,
        source: str,
        lookup_key: str,
    ) -> PublicDataCacheRecord | None:
        cache_key = (
            provider_category,
            normalize_provider_source(source),
            normalize_lookup_key(lookup_key),
        )
        record = self._records.get(cache_key)
        if record is None:
            return None
        if record.is_expired():
            self._records.pop(cache_key, None)
            return None
        return record

    def set(
        self,
        result: NormalizedPublicDataResult,
        *,
        ttl_seconds: int,
        refresh_policy: RefreshPolicy,
    ) -> PublicDataCacheRecord:
        retrieved_at = utc_now()
        expires_at = (
            retrieved_at + timedelta(seconds=ttl_seconds)
            if refresh_policy != "manual"
            else None
        )
        lookup_key = normalize_lookup_key(result.lookup_key)
        source = normalize_provider_source(result.source)
        record = PublicDataCacheRecord(
            provider_category=result.provider_category,
            source=source,
            lookup_key=lookup_key,
            response=result.model_copy(update={"lookup_key": lookup_key}),
            retrieved_at=retrieved_at,
            expires_at=expires_at,
            refresh_policy=refresh_policy,
        )
        self._records[(record.provider_category, record.source, record.lookup_key)] = (
            record
        )
        return record


class PublicDataFixtureStore:
    def __init__(
        self,
        fixtures: list[NormalizedPublicDataResult] | None = None,
    ) -> None:
        self._fixtures: dict[
            tuple[ProviderCategory, str, str], NormalizedPublicDataResult
        ] = {}
        for fixture in fixtures or []:
            self.add(fixture)

    def add(self, fixture: NormalizedPublicDataResult) -> None:
        key = (
            fixture.provider_category,
            normalize_provider_source(fixture.source),
            normalize_lookup_key(fixture.lookup_key),
        )
        self._fixtures[key] = fixture.model_copy(
            update={
                "lookup_key": key[2],
                "is_fixture": True,
                "cache_hit": False,
            }
        )

    def get(
        self,
        provider_category: ProviderCategory,
        source: str,
        lookup_key: str,
        *,
        warning: ProviderWarning,
    ) -> NormalizedPublicDataResult | None:
        key = (
            provider_category,
            normalize_provider_source(source),
            normalize_lookup_key(lookup_key),
        )
        fixture = self._fixtures.get(key)
        if fixture is None:
            return None
        return fixture.model_copy(
            update={
                "lookup_key": key[2],
                "retrieved_at": utc_now(),
                "warnings": [*fixture.warnings, warning],
                "is_fixture": True,
                "cache_hit": False,
            },
        )


class PublicDataAdapterConfig(BaseModel):
    use_fixtures: bool = True
    api_key: SecretStr | str | None = None
    requires_api_key: bool = False
    timeout_seconds: float = Field(default=8.0, gt=0, le=60)
    cache_ttl_seconds: int = Field(default=86_400, gt=0)
    refresh_policy: RefreshPolicy = "ttl"

    @property
    def has_api_key(self) -> bool:
        return _secret_is_configured(self.api_key)


class ProviderBoundaryError(Exception):
    code: ProviderWarningCode = "provider_error"
    retryable = False

    def __init__(self, provider_category: ProviderCategory) -> None:
        self.provider_category = provider_category
        super().__init__(SANITIZED_WARNING_MESSAGES[self.code])

    def to_warning(self) -> ProviderWarning:
        return ProviderWarning.from_code(
            self.provider_category,
            self.code,
            retryable=self.retryable,
        )


class ProviderTimeoutError(ProviderBoundaryError):
    code: ProviderWarningCode = "timeout"
    retryable = True


class ProviderSchemaChangedError(ProviderBoundaryError):
    code: ProviderWarningCode = "schema_changed"


class ProviderRateLimitError(ProviderBoundaryError):
    code: ProviderWarningCode = "rate_limited"
    retryable = True


class BasePublicDataAdapter:
    provider_category: ProviderCategory
    source_name: str

    def __init__(
        self,
        *,
        config: PublicDataAdapterConfig,
        fixture_store: PublicDataFixtureStore,
        cache: InMemoryPublicDataCache | None = None,
    ) -> None:
        self.config = config
        self.fixture_store = fixture_store
        self.cache = cache or InMemoryPublicDataCache()

    async def lookup(self, lookup_key: str) -> NormalizedPublicDataResult:
        normalized_key = normalize_lookup_key(lookup_key)
        cached = self.cache.get(
            self.provider_category,
            self.source_name,
            normalized_key,
        )
        if cached is not None:
            return cached.response.model_copy(update={"cache_hit": True})

        if self.config.requires_api_key and not self.config.has_api_key:
            return self._fixture_or_no_data(normalized_key, "missing_key")

        if self.config.use_fixtures:
            return self._fixture_or_no_data(normalized_key, "fixture_selected")

        try:
            result = await self.fetch_normalized(normalized_key)
        except ProviderBoundaryError as exc:
            return self._fixture_or_no_data(normalized_key, exc.code, exc.to_warning())
        except (TimeoutError, httpx.TimeoutException):
            return self._fixture_or_no_data(normalized_key, "timeout")
        except (KeyError, TypeError, ValueError):
            return self._fixture_or_no_data(normalized_key, "schema_changed")
        except httpx.HTTPStatusError as exc:
            warning_code: ProviderWarningCode = (
                "rate_limited" if exc.response.status_code == 429 else "provider_error"
            )
            return self._fixture_or_no_data(normalized_key, warning_code)
        except httpx.HTTPError:
            return self._fixture_or_no_data(normalized_key, "provider_error")

        normalized = result.model_copy(
            update={
                "provider_category": self.provider_category,
                "source": self.source_name,
                "lookup_key": normalized_key,
                "is_fixture": False,
                "cache_hit": False,
            }
        )
        self.cache.set(
            normalized,
            ttl_seconds=self.config.cache_ttl_seconds,
            refresh_policy=self.config.refresh_policy,
        )
        return normalized

    async def fetch_normalized(self, lookup_key: str) -> NormalizedPublicDataResult:
        raise NotImplementedError

    def _fixture_or_no_data(
        self,
        lookup_key: str,
        code: ProviderWarningCode,
        warning: ProviderWarning | None = None,
    ) -> NormalizedPublicDataResult:
        degraded_warning = warning or ProviderWarning.from_code(
            self.provider_category,
            code,
            retryable=code in {"timeout", "rate_limited"},
        )
        fixture = self.fixture_store.get(
            self.provider_category,
            self.source_name,
            lookup_key,
            warning=degraded_warning,
        )
        if fixture is not None:
            self.cache.set(
                fixture,
                ttl_seconds=self.config.cache_ttl_seconds,
                refresh_policy=self.config.refresh_policy,
            )
            return fixture

        return NormalizedPublicDataResult(
            provider_category=self.provider_category,
            lookup_key=lookup_key,
            source=self.source_name,
            warnings=[
                degraded_warning,
                ProviderWarning.from_code(
                    self.provider_category,
                    "fixture_unavailable",
                ),
            ],
        )


@dataclass(frozen=True)
class PublicDataClientConfig:
    use_fixtures: bool = True
    news_api_key: str | None = None
    fred_api_key: str | None = None
    timeout_seconds: float = 8.0
    cache_ttl_seconds: int = 86_400


@dataclass(frozen=True)
class PublicEnrichmentResult:
    enrichment: Enrichment
    warnings: list[str] = field(default_factory=list)
    degraded_reasons: list[str] = field(default_factory=list)
    activity_entries: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class _GeoResult:
    market: str
    coordinates: tuple[float, float] | None
    geo_confidence: str | None
    census_geo_id: str | None
    facts: list[SourceFact]


@dataclass(frozen=True)
class _CompanyResult:
    company_units: int | None
    asset_type_fit: str
    facts: list[SourceFact]


PERSONAL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "icloud.com",
    "aol.com",
}

FIXTURE_COORDINATES: dict[tuple[str, str, str], tuple[float, float]] = {
    ("100 main st", "austin", "tx"): (30.2672, -97.7431),
    ("100 market st", "austin", "tx"): (30.2672, -97.7431),
    ("200 market st", "dallas", "tx"): (32.7767, -96.7970),
    ("300 market st", "boise", "id"): (43.6150, -116.2023),
    ("400 market st", "austin", "tx"): (30.2672, -97.7431),
    ("500 market st", "dallas", "tx"): (32.7767, -96.7970),
    ("123 market st", "austin", "tx"): (30.2672, -97.7431),
    ("123 market st", "charlotte", "nc"): (35.2271, -80.8431),
    ("123 market st", "raleigh", "nc"): (35.7796, -78.6382),
}


class PublicDataClient:
    """Normalizes public-data categories into display-safe enrichment facts."""

    def __init__(
        self,
        config: PublicDataClientConfig,
        *,
        cache: InMemoryPublicDataCache | None = None,
        fixture_store: PublicDataFixtureStore | None = None,
    ) -> None:
        self.config = config
        self.cache = cache or InMemoryPublicDataCache()
        self.fixture_store = fixture_store or PublicDataFixtureStore()

    async def enrich(self, lead: LeadCreate) -> PublicEnrichmentResult:
        retrieved_at = utc_now()
        warnings: list[str] = []
        degraded_reasons: list[str] = []

        geo = await self._geocode(lead, retrieved_at, warnings, degraded_reasons)
        demographics = self._fixture_demographics(lead, retrieved_at)
        economics = self._fixture_economics(lead, retrieved_at)
        local_context = self._fixture_local_context(lead, retrieved_at)
        company = self._fixture_company_context(lead.company, retrieved_at)
        trigger = self._fixture_trigger_context(
            lead,
            company.company_units,
            retrieved_at,
        )
        domain = await self._domain_quality(
            lead,
            retrieved_at,
            warnings,
            degraded_reasons,
        )

        if local_context["walkability_score"] is None:
            warnings.append("local context unavailable")
            degraded_reasons.append("local_context: fixture no-data")
        if trigger["recent_trigger"] is None:
            warnings.append("trigger context unavailable")
            degraded_reasons.append("trigger_context: fixture no-data")

        sources = [
            *geo.facts,
            *demographics["facts"],
            *economics["facts"],
            *local_context["facts"],
            *company.facts,
            *trigger["facts"],
            *domain["facts"],
        ]
        return PublicEnrichmentResult(
            enrichment=Enrichment(
                market=geo.market,
                coordinates=geo.coordinates,
                geo_confidence=geo.geo_confidence,
                census_geo_id=geo.census_geo_id,
                renter_share=demographics["renter_share"],
                median_rent=economics["median_rent"],
                rent_growth_yoy=economics["rent_growth_yoy"],
                household_growth=demographics["household_growth"],
                unemployment_rate=economics["unemployment_rate"],
                walkability_score=local_context["walkability_score"],
                company_units=company.company_units,
                asset_type_fit=company.asset_type_fit,
                recent_trigger=trigger["recent_trigger"],
                domain_status=domain["domain_status"],
                sources=sources,
            ),
            warnings=warnings,
            degraded_reasons=degraded_reasons,
            activity_entries=[
                "public_data: geocoding normalized",
                "public_data: demographics normalized",
                "public_data: economics normalized",
                "public_data: local_context normalized",
                "public_data: company_context normalized",
                "public_data: trigger_context normalized",
                "public_data: domain_quality normalized",
            ],
        )

    async def _geocode(
        self,
        lead: LeadCreate,
        retrieved_at: datetime,
        warnings: list[str],
        degraded_reasons: list[str],
    ) -> _GeoResult:
        if self.config.use_fixtures:
            return self._fixture_geocode(lead, retrieved_at)
        lookup_key = self._geocode_lookup_key(lead)
        cached = self.cache.get("geocoding", "nominatim", lookup_key)
        if cached is not None:
            return self._geo_from_normalized(
                cached.response.model_copy(update={"cache_hit": True}),
                lead,
            )
        try:
            result = await self._live_geocode(lead, retrieved_at)
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            warnings.append("geocoding fixture fallback")
            degraded_reasons.append("geocoding: fixture fallback")
            return self._fixture_geocode(lead, retrieved_at)
        self.cache.set(
            self._normalized_geocode_result(lookup_key, result),
            ttl_seconds=self.config.cache_ttl_seconds,
            refresh_policy="ttl",
        )
        return result

    async def _live_geocode(
        self,
        lead: LeadCreate,
        retrieved_at: datetime,
    ) -> _GeoResult:
        query = self._geocode_lookup_key(lead)
        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "jsonv2", "limit": "1"},
                headers={"User-Agent": "signal-public-data/1.0"},
            )
            response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list) or not payload:
            raise ValueError("no geocoding result")
        first = payload[0]
        latitude = float(first["lat"])
        longitude = float(first["lon"])
        return _GeoResult(
            market=f"{lead.city}, {lead.state}",
            coordinates=(latitude, longitude),
            geo_confidence="high",
            census_geo_id=None,
            facts=[
                _fact(
                    source="geocoding",
                    label="Address resolution",
                    value="resolved",
                    retrieved_at=retrieved_at,
                    confidence="high",
                )
            ],
        )

    def _geocode_lookup_key(self, lead: LeadCreate) -> str:
        return ", ".join(
            [
                lead.property_address,
                lead.city,
                lead.state,
                lead.country,
            ]
        )

    def _normalized_geocode_result(
        self,
        lookup_key: str,
        result: _GeoResult,
    ) -> NormalizedPublicDataResult:
        latitude: float | None = None
        longitude: float | None = None
        if result.coordinates is not None:
            latitude, longitude = result.coordinates
        return NormalizedPublicDataResult(
            provider_category="geocoding",
            lookup_key=lookup_key,
            source="nominatim",
            data={
                "market": result.market,
                "latitude": latitude,
                "longitude": longitude,
                "geo_confidence": result.geo_confidence,
                "census_geo_id": result.census_geo_id,
            },
            facts=result.facts,
        )

    def _geo_from_normalized(
        self,
        result: NormalizedPublicDataResult,
        lead: LeadCreate,
    ) -> _GeoResult:
        latitude = result.data.get("latitude")
        longitude = result.data.get("longitude")
        coordinates = (
            (float(latitude), float(longitude))
            if latitude is not None and longitude is not None
            else None
        )
        market = result.data.get("market")
        geo_confidence = result.data.get("geo_confidence")
        census_geo_id = result.data.get("census_geo_id")
        market_value = (
            str(market) if isinstance(market, str) else f"{lead.city}, {lead.state}"
        )
        census_geo_id_value = (
            str(census_geo_id) if isinstance(census_geo_id, str) else None
        )
        return _GeoResult(
            market=market_value,
            coordinates=coordinates,
            geo_confidence=(
                str(geo_confidence) if isinstance(geo_confidence, str) else None
            ),
            census_geo_id=census_geo_id_value,
            facts=result.facts,
        )

    def _fixture_geocode(self, lead: LeadCreate, retrieved_at: datetime) -> _GeoResult:
        market = f"{lead.city}, {lead.state}"
        supported_country = lead.country.upper() in {"US", "USA", "UNITED STATES"}
        location_key = (
            normalize_lookup_key(lead.property_address),
            normalize_lookup_key(lead.city),
            normalize_lookup_key(lead.state),
        )
        coordinates = (
            FIXTURE_COORDINATES.get(location_key) if supported_country else None
        )
        confidence = "high" if coordinates else None
        value = "resolved" if coordinates else "unresolved"
        return _GeoResult(
            market=market if coordinates else "",
            coordinates=coordinates,
            geo_confidence=confidence,
            census_geo_id=(
                f"fixture-{location_key[1]}-{location_key[2]}"
                if coordinates
                else None
            ),
            facts=[
                _fact(
                    source="geocoding",
                    label="Address resolution",
                    value=value,
                    retrieved_at=retrieved_at,
                    confidence="high" if coordinates else "low",
                )
            ],
        )

    def _fixture_demographics(
        self,
        lead: LeadCreate,
        retrieved_at: datetime,
    ) -> dict[str, object]:
        city_key = lead.city.lower()
        renter_share = 0.61 if city_key in {"austin", "arlington"} else 0.48
        household_growth = 4.4 if city_key in {"austin", "raleigh"} else 2.8
        return {
            "renter_share": renter_share,
            "household_growth": household_growth,
            "facts": [
                _fact(
                    source="demographics",
                    label="Renter share",
                    value=f"{renter_share:.0%}",
                    retrieved_at=retrieved_at,
                    confidence="high",
                ),
                _fact(
                    source="demographics",
                    label="Household growth",
                    value=f"{household_growth:.1f}%",
                    retrieved_at=retrieved_at,
                    confidence="medium",
                ),
            ],
        }

    def _fixture_economics(
        self,
        lead: LeadCreate,
        retrieved_at: datetime,
    ) -> dict[str, object]:
        city_key = lead.city.lower()
        rent_growth = 8.1 if city_key in {"austin", "charlotte"} else 3.4
        median_rent = 1840 if city_key in {"austin", "raleigh"} else 1525
        unemployment_rate = 3.2 if city_key in {"austin", "raleigh"} else 4.6
        return {
            "median_rent": median_rent,
            "rent_growth_yoy": rent_growth,
            "unemployment_rate": unemployment_rate,
            "facts": [
                _fact(
                    source="economics",
                    label="Median rent",
                    value=f"${median_rent:,}",
                    retrieved_at=retrieved_at,
                    confidence="medium",
                ),
                _fact(
                    source="economics",
                    label="Rent growth",
                    value=f"{rent_growth:.1f}% YoY",
                    retrieved_at=retrieved_at,
                    confidence="medium",
                ),
                _fact(
                    source="economics",
                    label="Unemployment rate",
                    value=f"{unemployment_rate:.1f}%",
                    retrieved_at=retrieved_at,
                    confidence="medium",
                ),
            ],
        }

    def _fixture_local_context(
        self,
        lead: LeadCreate,
        retrieved_at: datetime,
    ) -> dict[str, object]:
        city_key = lead.city.lower()
        walkability_score = None if city_key == "raleigh" else 72
        return {
            "walkability_score": walkability_score,
            "facts": [
                _fact(
                    source="local_context",
                    label="Walkability score",
                    value=(
                        str(walkability_score)
                        if walkability_score is not None
                        else "No local context available"
                    ),
                    retrieved_at=retrieved_at,
                    confidence="fallback" if walkability_score is None else "medium",
                )
            ],
        }

    def _fixture_company_context(
        self,
        company: str,
        retrieved_at: datetime,
    ) -> _CompanyResult:
        company_units = _company_units(company)
        asset_type_fit = "multifamily" if company_units else "unclear"
        value = f"{company_units:,}" if company_units is not None else "unresolved"
        return _CompanyResult(
            company_units=company_units,
            asset_type_fit=asset_type_fit,
            facts=[
                _fact(
                    source="company_context",
                    label="Company units",
                    value=value,
                    retrieved_at=retrieved_at,
                    confidence="fallback",
                ),
                _fact(
                    source="company_context",
                    label="Asset type fit",
                    value=asset_type_fit,
                    retrieved_at=retrieved_at,
                    confidence="fallback",
                ),
            ],
        )

    def _fixture_trigger_context(
        self,
        lead: LeadCreate,
        company_units: int | None,
        retrieved_at: datetime,
    ) -> dict[str, object]:
        recent_trigger = (
            f"{lead.company} announced regional portfolio expansion"
            if (
                company_units
                and company_units >= 50000
                and lead.city.lower() != "raleigh"
            )
            else None
        )
        return {
            "recent_trigger": recent_trigger,
            "facts": [
                _fact(
                    source="trigger_context",
                    label="Trigger event",
                    value=recent_trigger or "No recent trigger found",
                    retrieved_at=retrieved_at,
                    confidence="medium" if recent_trigger else "fallback",
                )
            ],
        }

    def _fixture_domain_quality(
        self,
        lead: LeadCreate,
        retrieved_at: datetime,
    ) -> dict[str, object]:
        domain = lead.email.split("@")[-1].lower()
        if domain in PERSONAL_DOMAINS:
            status = "personal"
        elif "." not in domain:
            status = "invalid"
        else:
            status = "corporate"
        return {
            "domain_status": status,
            "facts": [
                _fact(
                    source="domain_quality",
                    label="Domain quality",
                    value=status,
                    retrieved_at=retrieved_at,
                    confidence="medium",
                )
            ],
        }

    async def _domain_quality(
        self,
        lead: LeadCreate,
        retrieved_at: datetime,
        warnings: list[str],
        degraded_reasons: list[str],
    ) -> dict[str, object]:
        if self.config.use_fixtures:
            return self._fixture_domain_quality(lead, retrieved_at)
        domain = self._domain_lookup_key(lead)
        cached = self.cache.get("domain_quality", "dns_mx", domain)
        if cached is not None:
            return self._domain_from_normalized(
                cached.response.model_copy(update={"cache_hit": True})
            )
        try:
            result = await self._live_domain_quality(lead, retrieved_at)
        except (dns.exception.DNSException, TimeoutError, OSError):
            warnings.append("domain quality unavailable")
            degraded_reasons.append("domain_quality: provider unavailable")
            return self._unknown_domain_quality(retrieved_at)
        self.cache.set(
            self._normalized_domain_result(domain, result),
            ttl_seconds=self.config.cache_ttl_seconds,
            refresh_policy="ttl",
        )
        return result

    async def _live_domain_quality(
        self,
        lead: LeadCreate,
        retrieved_at: datetime,
    ) -> dict[str, object]:
        domain = self._domain_lookup_key(lead)
        if domain in PERSONAL_DOMAINS:
            status = "personal"
        elif "." not in domain:
            status = "invalid"
        else:
            try:
                answers = await dns.asyncresolver.resolve(domain, "MX")
            except dns.resolver.NXDOMAIN:
                status = "invalid"
            except dns.resolver.NoAnswer:
                status = "unknown"
            else:
                status = "corporate" if answers else "unknown"
        return {
            "domain_status": status,
            "facts": [
                _fact(
                    source="domain_quality",
                    label="Domain quality",
                    value=status,
                    retrieved_at=retrieved_at,
                    confidence="high" if status == "corporate" else "medium",
                )
            ],
        }

    def _domain_lookup_key(self, lead: LeadCreate) -> str:
        return lead.email.split("@")[-1].lower()

    def _unknown_domain_quality(self, retrieved_at: datetime) -> dict[str, object]:
        return {
            "domain_status": "unknown",
            "facts": [
                _fact(
                    source="domain_quality",
                    label="Domain quality",
                    value="unknown",
                    retrieved_at=retrieved_at,
                    confidence="low",
                )
            ],
        }

    def _normalized_domain_result(
        self,
        lookup_key: str,
        result: dict[str, object],
    ) -> NormalizedPublicDataResult:
        domain_status = result.get("domain_status")
        return NormalizedPublicDataResult(
            provider_category="domain_quality",
            lookup_key=lookup_key,
            source="dns_mx",
            data={
                "domain_status": (
                    domain_status if isinstance(domain_status, str) else "unknown"
                )
            },
            facts=[
                fact
                for fact in result.get("facts", [])
                if isinstance(fact, SourceFact)
            ],
        )

    def _domain_from_normalized(
        self,
        result: NormalizedPublicDataResult,
    ) -> dict[str, object]:
        domain_status = result.data.get("domain_status")
        return {
            "domain_status": (
                domain_status if isinstance(domain_status, str) else "unknown"
            ),
            "facts": result.facts,
        }


def _fact(
    *,
    source: str,
    label: str,
    value: str,
    retrieved_at: datetime,
    confidence: str,
    url: str | None = None,
) -> SourceFact:
    return SourceFact(
        source=source,
        label=label,
        value=value,
        url=url,
        retrieved_at=retrieved_at,
        confidence=confidence,
    )


def _company_units(company: str) -> int | None:
    normalized = company.lower()
    if any(token in normalized for token in ("residential", "living", "property")):
        return 85000
    if any(token in normalized for token in ("homes", "communities")):
        return 42000
    if any(token in normalized for token in ("housing", "apartments", "portfolio")):
        return 12000
    return None
