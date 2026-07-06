from datetime import datetime

import pytest

from app.integrations import public_data
from app.integrations.public_data import PublicDataClient, PublicDataClientConfig
from app.schemas.lead import LeadCreate


def _lead(**overrides: object) -> LeadCreate:
    values = {
        "contact_name": "Demo Contact",
        "email": "contact@operator.example",
        "company": "Regional Property Operator",
        "role": "VP Leasing",
        "property_address": "123 Market St",
        "city": "Austin",
        "state": "TX",
        "country": "US",
    }
    values.update(overrides)
    return LeadCreate(**values)


@pytest.mark.asyncio
async def test_public_data_client_normalizes_successful_fixture_facts() -> None:
    client = PublicDataClient(PublicDataClientConfig(use_fixtures=True))

    result = await client.enrich(_lead())

    assert result.enrichment.market == "Austin, TX"
    assert result.enrichment.coordinates is not None
    assert result.enrichment.geo_confidence == "high"
    assert result.enrichment.domain_status == "corporate"
    assert result.enrichment.company_units == 85000
    assert result.warnings == []
    assert result.degraded_reasons == []
    fact_labels = {fact.label for fact in result.enrichment.sources}
    assert fact_labels >= {
        "Address resolution",
        "Renter share",
        "Rent growth",
        "Company units",
        "Domain quality",
    }
    assert all(fact.value for fact in result.enrichment.sources)


@pytest.mark.asyncio
async def test_public_data_client_marks_optional_no_data_as_degraded() -> None:
    client = PublicDataClient(PublicDataClientConfig(use_fixtures=True))

    result = await client.enrich(_lead(city="Raleigh", state="NC"))

    assert result.enrichment.market == "Raleigh, NC"
    assert result.enrichment.coordinates is not None
    assert result.enrichment.recent_trigger is None
    assert result.enrichment.walkability_score is None
    assert "local context unavailable" in result.warnings
    assert "trigger context unavailable" in result.warnings
    assert result.degraded_reasons == [
        "local_context: fixture no-data",
        "trigger_context: fixture no-data",
    ]
    assert any(
        fact.label == "Trigger event" and fact.confidence == "fallback"
        for fact in result.enrichment.sources
    )


@pytest.mark.asyncio
async def test_public_data_client_flags_personal_domain_quality() -> None:
    client = PublicDataClient(PublicDataClientConfig(use_fixtures=True))

    result = await client.enrich(_lead(email="contact@gmail.com"))

    assert result.enrichment.domain_status == "personal"
    assert any(
        fact.label == "Domain quality" and fact.value == "personal"
        for fact in result.enrichment.sources
    )


@pytest.mark.asyncio
async def test_fixture_geocode_returns_no_data_for_unsupported_location() -> None:
    client = PublicDataClient(PublicDataClientConfig(use_fixtures=True))

    result = await client.enrich(_lead(city="Unsupported", state="TX"))

    assert result.enrichment.market == ""
    assert result.enrichment.coordinates is None
    assert result.enrichment.geo_confidence is None
    assert result.enrichment.census_geo_id is None
    assert any(
        fact.label == "Address resolution" and fact.value == "unresolved"
        for fact in result.enrichment.sources
    )


@pytest.mark.asyncio
async def test_fixture_geocode_returns_no_data_for_unmatched_address() -> None:
    client = PublicDataClient(PublicDataClientConfig(use_fixtures=True))

    result = await client.enrich(_lead(property_address="999 Missing Pl"))

    assert result.enrichment.market == ""
    assert result.enrichment.coordinates is None
    assert result.enrichment.geo_confidence is None
    assert any(
        fact.label == "Address resolution" and fact.value == "unresolved"
        for fact in result.enrichment.sources
    )


@pytest.mark.asyncio
async def test_live_geocode_provider_failure_uses_sanitized_fixture_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingAsyncClient:
        def __init__(self, *, timeout: float) -> None:
            self.timeout = timeout

        async def __aenter__(self) -> "FailingAsyncClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def get(self, *args: object, **kwargs: object) -> object:
            raise public_data.httpx.ConnectError("provider unavailable")

    monkeypatch.setattr(public_data.httpx, "AsyncClient", FailingAsyncClient)
    client = PublicDataClient(PublicDataClientConfig(use_fixtures=False))

    result = await client.enrich(_lead(city="Unsupported", state="TX"))

    assert result.enrichment.coordinates is None
    assert result.enrichment.geo_confidence is None
    assert "geocoding fixture fallback" in result.warnings
    assert "geocoding: fixture fallback" in result.degraded_reasons
    assert all("provider unavailable" not in warning for warning in result.warnings)


@pytest.mark.asyncio
async def test_live_geocode_no_data_fallback_requires_matching_fixture_address(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class NoDataResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> list[object]:
            return []

    class NoDataAsyncClient:
        def __init__(self, *, timeout: float) -> None:
            self.timeout = timeout

        async def __aenter__(self) -> "NoDataAsyncClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def get(self, *args: object, **kwargs: object) -> NoDataResponse:
            return NoDataResponse()

    monkeypatch.setattr(public_data.httpx, "AsyncClient", NoDataAsyncClient)
    client = PublicDataClient(PublicDataClientConfig(use_fixtures=False))

    result = await client.enrich(_lead(property_address="999 Missing Pl"))

    assert result.enrichment.coordinates is None
    assert result.enrichment.geo_confidence is None
    assert "geocoding fixture fallback" in result.warnings
    assert "geocoding: fixture fallback" in result.degraded_reasons


@pytest.mark.asyncio
async def test_live_domain_dns_failure_returns_gate_failing_unknown_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fixture_live_geocode(
        self: PublicDataClient,
        lead: LeadCreate,
        retrieved_at: datetime,
    ) -> object:
        return self._fixture_geocode(lead, retrieved_at)

    async def failing_resolve(domain: str, record_type: str) -> object:
        raise public_data.dns.exception.Timeout

    monkeypatch.setattr(PublicDataClient, "_live_geocode", fixture_live_geocode)
    monkeypatch.setattr(public_data.dns.asyncresolver, "resolve", failing_resolve)
    client = PublicDataClient(PublicDataClientConfig(use_fixtures=False))

    result = await client.enrich(_lead())

    assert result.enrichment.domain_status == "unknown"
    assert "domain quality unavailable" in result.warnings
    assert "domain_quality: provider unavailable" in result.degraded_reasons
    assert all("operator.example" not in warning for warning in result.warnings)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("dns_error", "expected_status"),
    [
        (public_data.dns.resolver.NXDOMAIN, "invalid"),
        (public_data.dns.resolver.NoAnswer, "unknown"),
    ],
)
async def test_live_domain_negative_dns_results_do_not_use_fixture_fallback(
    monkeypatch: pytest.MonkeyPatch,
    dns_error: type[Exception],
    expected_status: str,
) -> None:
    async def fixture_live_geocode(
        self: PublicDataClient,
        lead: LeadCreate,
        retrieved_at: datetime,
    ) -> object:
        return self._fixture_geocode(lead, retrieved_at)

    async def negative_resolve(domain: str, record_type: str) -> object:
        raise dns_error

    monkeypatch.setattr(PublicDataClient, "_live_geocode", fixture_live_geocode)
    monkeypatch.setattr(public_data.dns.asyncresolver, "resolve", negative_resolve)
    client = PublicDataClient(PublicDataClientConfig(use_fixtures=False))

    result = await client.enrich(_lead(email="contact@missing-domain.example"))

    assert result.enrichment.domain_status == expected_status
    assert "domain-quality fixture fallback" not in result.warnings
    assert "domain_quality: fixture fallback" not in result.degraded_reasons
    assert any(
        fact.label == "Domain quality" and fact.value == expected_status
        for fact in result.enrichment.sources
    )


@pytest.mark.asyncio
async def test_live_geocode_success_uses_cache_on_repeat_lookup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    class SuccessResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> list[dict[str, str]]:
            return [{"lat": "30.2672", "lon": "-97.7431"}]

    class SuccessAsyncClient:
        def __init__(self, *, timeout: float) -> None:
            self.timeout = timeout

        async def __aenter__(self) -> "SuccessAsyncClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def get(self, *args: object, **kwargs: object) -> SuccessResponse:
            nonlocal calls
            calls += 1
            return SuccessResponse()

    monkeypatch.setattr(public_data.httpx, "AsyncClient", SuccessAsyncClient)
    client = PublicDataClient(PublicDataClientConfig(use_fixtures=False))
    lead = _lead(email="contact@gmail.com")

    first = await client.enrich(lead)
    second = await client.enrich(lead)

    assert first.enrichment.coordinates == (30.2672, -97.7431)
    assert second.enrichment.coordinates == (30.2672, -97.7431)
    assert calls == 1


@pytest.mark.asyncio
async def test_live_domain_success_uses_cache_on_repeat_lookup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    async def fixture_live_geocode(
        self: PublicDataClient,
        lead: LeadCreate,
        retrieved_at: datetime,
    ) -> object:
        return self._fixture_geocode(lead, retrieved_at)

    async def successful_resolve(domain: str, record_type: str) -> list[object]:
        nonlocal calls
        calls += 1
        return [object()]

    monkeypatch.setattr(PublicDataClient, "_live_geocode", fixture_live_geocode)
    monkeypatch.setattr(public_data.dns.asyncresolver, "resolve", successful_resolve)
    client = PublicDataClient(PublicDataClientConfig(use_fixtures=False))
    lead = _lead()

    first = await client.enrich(lead)
    second = await client.enrich(lead)

    assert first.enrichment.domain_status == "corporate"
    assert second.enrichment.domain_status == "corporate"
    assert calls == 1
