from dataclasses import dataclass, field
from datetime import UTC, datetime

import dns.asyncresolver
import dns.exception
import httpx

from app.schemas.lead import Enrichment, LeadCreate, SourceFact


@dataclass(frozen=True)
class PublicDataClientConfig:
    use_fixtures: bool = True
    news_api_key: str | None = None
    fred_api_key: str | None = None
    timeout_seconds: float = 8.0


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

FIXTURE_COORDINATES: dict[tuple[str, str], tuple[float, float]] = {
    ("austin", "tx"): (30.2672, -97.7431),
    ("arlington", "tx"): (32.7357, -97.1081),
    ("charlotte", "nc"): (35.2271, -80.8431),
    ("raleigh", "nc"): (35.7796, -78.6382),
}


class PublicDataClient:
    """Normalizes public-data categories into display-safe enrichment facts."""

    def __init__(self, config: PublicDataClientConfig) -> None:
        self.config = config

    async def enrich(self, lead: LeadCreate) -> PublicEnrichmentResult:
        retrieved_at = datetime.now(UTC)
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
        try:
            return await self._live_geocode(lead, retrieved_at)
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            warnings.append("geocoding fixture fallback")
            degraded_reasons.append("geocoding: fixture fallback")
            return self._fixture_geocode(lead, retrieved_at)

    async def _live_geocode(
        self,
        lead: LeadCreate,
        retrieved_at: datetime,
    ) -> _GeoResult:
        query = ", ".join(
            [
                lead.property_address,
                lead.city,
                lead.state,
                lead.country,
            ]
        )
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

    def _fixture_geocode(self, lead: LeadCreate, retrieved_at: datetime) -> _GeoResult:
        market = f"{lead.city}, {lead.state}"
        supported_country = lead.country.upper() in {"US", "USA", "UNITED STATES"}
        unresolved = "unresolved" in lead.property_address.lower()
        location_key = (lead.city.lower(), lead.state.lower())
        coordinates = (
            FIXTURE_COORDINATES.get(location_key)
            if supported_country and not unresolved
            else None
        )
        confidence = "high" if coordinates else None
        value = "resolved" if coordinates else "unresolved"
        return _GeoResult(
            market=market if coordinates else "",
            coordinates=coordinates,
            geo_confidence=confidence,
            census_geo_id=(
                f"fixture-{location_key[0]}-{location_key[1]}"
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
        try:
            return await self._live_domain_quality(lead, retrieved_at)
        except (dns.exception.DNSException, TimeoutError, OSError):
            warnings.append("domain-quality fixture fallback")
            degraded_reasons.append("domain_quality: fixture fallback")
            return self._fixture_domain_quality(lead, retrieved_at)

    async def _live_domain_quality(
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
            answers = await dns.asyncresolver.resolve(domain, "MX")
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
    if any(token in normalized for token in ("housing", "apartments")):
        return 12000
    return None
