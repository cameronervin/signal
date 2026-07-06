from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

import httpx
from pydantic import BaseModel, Field, SecretStr

from app.schemas.lead import SourceFact

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


class PublicDataClient:
    """Container for public-data adapters shared by enrichment services."""

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
