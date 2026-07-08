from dataclasses import dataclass


@dataclass(frozen=True)
class GeocodingResult:
    display_name: str
    latitude: float
    longitude: float
    city: str | None = None
    state: str | None = None


@dataclass(frozen=True)
class CensusMarketSnapshot:
    renter_share: float | None = None
    median_rent: int | None = None
    household_count: int | None = None
    household_growth: float | None = None
    source_name: str = "Census ACS"


@dataclass(frozen=True)
class FredSnapshot:
    rent_growth_yoy: float | None = None
    unemployment_rate: float | None = None
    source_name: str = "FRED"


@dataclass(frozen=True)
class NewsSnapshot:
    trigger: str | None = None
    url: str | None = None
    source_name: str = "News API"


@dataclass(frozen=True)
class CompanySnapshot:
    summary: str | None = None
    url: str | None = None
    source_name: str = "Wikipedia"


@dataclass(frozen=True)
class DomainSnapshot:
    has_mx: bool | None = None
    source_name: str = "DNS MX"
