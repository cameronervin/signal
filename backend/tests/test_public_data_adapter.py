from datetime import UTC, datetime

import pytest

from app.integrations.public_data import (
    BasePublicDataAdapter,
    InMemoryPublicDataCache,
    NormalizedPublicDataResult,
    ProviderTimeoutError,
    PublicDataAdapterConfig,
    PublicDataFixtureStore,
)
from app.schemas.lead import SourceFact


class StubPublicDataAdapter(BasePublicDataAdapter):
    provider_category = "company_context"
    source_name = "stub source"

    def __init__(
        self,
        config: PublicDataAdapterConfig,
        fixture_store: PublicDataFixtureStore,
        cache: InMemoryPublicDataCache | None = None,
        *,
        should_timeout: bool = False,
        employee_range: str = "1000+",
    ) -> None:
        super().__init__(config=config, fixture_store=fixture_store, cache=cache)
        self.should_timeout = should_timeout
        self.employee_range = employee_range
        self.fetch_count = 0

    async def fetch_normalized(self, lookup_key: str) -> NormalizedPublicDataResult:
        self.fetch_count += 1
        if self.should_timeout:
            raise ProviderTimeoutError(provider_category=self.provider_category)
        return NormalizedPublicDataResult(
            provider_category=self.provider_category,
            lookup_key=lookup_key,
            source=self.source_name,
            data={"employee_range": self.employee_range},
            facts=[
                SourceFact(
                    source=self.source_name,
                    label="Scale hint",
                    value=self.employee_range,
                    retrieved_at=datetime.now(UTC),
                    confidence="medium",
                )
            ],
        )


class AlternateCompanyContextAdapter(StubPublicDataAdapter):
    provider_category = "company_context"
    source_name = "alternate source"


def fixture_store() -> PublicDataFixtureStore:
    store = PublicDataFixtureStore()
    store.add(
        NormalizedPublicDataResult(
            provider_category="company_context",
            lookup_key="regional operator",
            source="stub source",
            data={"employee_range": "fixture"},
            facts=[
                SourceFact(
                    source="fixture source",
                    label="Scale hint",
                    value="fixture",
                    retrieved_at=datetime.now(UTC),
                    confidence="fallback",
                )
            ],
        )
    )
    return store


@pytest.mark.asyncio
async def test_adapter_returns_normalized_success_and_cache_record() -> None:
    cache = InMemoryPublicDataCache()
    adapter = StubPublicDataAdapter(
        config=PublicDataAdapterConfig(api_key="configured", use_fixtures=False),
        fixture_store=fixture_store(),
        cache=cache,
    )

    result = await adapter.lookup(" Regional Operator ")
    cached = cache.get("company_context", "stub source", "regional operator")

    assert result.lookup_key == "regional operator"
    assert result.provider_category == "company_context"
    assert result.source == "stub source"
    assert result.facts[0].source == "stub source"
    assert result.data == {"employee_range": "1000+"}
    assert result.warnings == []
    assert result.is_fixture is False
    assert result.cache_hit is False
    assert cached is not None
    assert cached.provider_category == "company_context"
    assert cached.source == "stub source"
    assert cached.lookup_key == "regional operator"
    assert cached.response == result
    assert cached.retrieved_at is not None
    assert cached.expires_at is not None
    assert cached.refresh_policy == "ttl"

    second_result = await adapter.lookup("regional operator")

    assert second_result.cache_hit is True
    assert adapter.fetch_count == 1


@pytest.mark.asyncio
async def test_cache_keeps_same_category_adapter_results_separate_by_source() -> None:
    cache = InMemoryPublicDataCache()
    store = fixture_store()
    primary = StubPublicDataAdapter(
        config=PublicDataAdapterConfig(api_key="configured", use_fixtures=False),
        fixture_store=store,
        cache=cache,
        employee_range="primary",
    )
    fallback = AlternateCompanyContextAdapter(
        config=PublicDataAdapterConfig(api_key="configured", use_fixtures=False),
        fixture_store=store,
        cache=cache,
        employee_range="fallback",
    )

    primary_result = await primary.lookup("Regional Operator")
    fallback_result = await fallback.lookup("Regional Operator")

    assert primary_result.source == "stub source"
    assert primary_result.data == {"employee_range": "primary"}
    assert fallback_result.source == "alternate source"
    assert fallback_result.data == {"employee_range": "fallback"}

    primary_cached = await primary.lookup("regional operator")
    fallback_cached = await fallback.lookup("regional operator")

    assert primary_cached.cache_hit is True
    assert primary_cached.data == {"employee_range": "primary"}
    assert fallback_cached.cache_hit is True
    assert fallback_cached.data == {"employee_range": "fallback"}
    assert primary.fetch_count == 1
    assert fallback.fetch_count == 1


@pytest.mark.asyncio
async def test_fixture_store_keeps_same_category_fixtures_separate_by_source() -> None:
    store = PublicDataFixtureStore(
        fixtures=[
            NormalizedPublicDataResult(
                provider_category="company_context",
                lookup_key="regional operator",
                source="stub source",
                data={"employee_range": "primary fixture"},
            ),
            NormalizedPublicDataResult(
                provider_category="company_context",
                lookup_key="regional operator",
                source="alternate source",
                data={"employee_range": "fallback fixture"},
            ),
        ]
    )
    primary = StubPublicDataAdapter(
        config=PublicDataAdapterConfig(api_key=None, requires_api_key=True),
        fixture_store=store,
    )
    fallback = AlternateCompanyContextAdapter(
        config=PublicDataAdapterConfig(api_key=None, requires_api_key=True),
        fixture_store=store,
    )

    primary_result = await primary.lookup("Regional Operator")
    fallback_result = await fallback.lookup("Regional Operator")

    assert primary_result.is_fixture is True
    assert primary_result.source == "stub source"
    assert primary_result.data == {"employee_range": "primary fixture"}
    assert fallback_result.is_fixture is True
    assert fallback_result.source == "alternate source"
    assert fallback_result.data == {"employee_range": "fallback fixture"}
    assert primary.fetch_count == 0
    assert fallback.fetch_count == 0


@pytest.mark.asyncio
async def test_adapter_uses_fixture_for_missing_key_without_raw_detail() -> None:
    adapter = StubPublicDataAdapter(
        config=PublicDataAdapterConfig(api_key=None, requires_api_key=True),
        fixture_store=fixture_store(),
    )

    result = await adapter.lookup("regional operator")

    assert result.is_fixture is True
    assert result.source == "stub source"
    assert result.facts[0].confidence == "fallback"
    assert result.warnings[0].code == "missing_key"
    assert result.warnings[0].message == "Provider configuration is unavailable."
    assert "regional operator" not in result.warnings[0].message
    assert adapter.fetch_count == 0


@pytest.mark.asyncio
async def test_public_data_adapter_uses_fixture_for_timeout() -> None:
    adapter = StubPublicDataAdapter(
        config=PublicDataAdapterConfig(api_key="configured", use_fixtures=False),
        fixture_store=fixture_store(),
        should_timeout=True,
    )

    result = await adapter.lookup("regional operator")

    assert result.is_fixture is True
    assert result.source == "stub source"
    assert result.warnings[0].code == "timeout"
    assert result.warnings[0].retryable is True


@pytest.mark.asyncio
async def test_adapter_returns_sanitized_no_data_when_fixture_missing() -> None:
    adapter = StubPublicDataAdapter(
        config=PublicDataAdapterConfig(api_key=None, requires_api_key=True),
        fixture_store=PublicDataFixtureStore(),
    )

    result = await adapter.lookup("unknown operator")

    assert result.is_fixture is False
    assert result.facts == []
    assert result.data == {}
    assert [warning.code for warning in result.warnings] == [
        "missing_key",
        "fixture_unavailable",
    ]
    assert all("unknown operator" not in warning.message for warning in result.warnings)
