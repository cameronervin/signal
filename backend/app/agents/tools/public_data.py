"""Public-data tool wrappers for Signal graph nodes and agent research."""

from __future__ import annotations

from typing import Annotated, Literal

from langchain_core.tools import InjectedToolArg, StructuredTool
from pydantic import BaseModel, Field

from app.infrastructure.public_data import PublicDataClient
from app.infrastructure.public_data.provider import (
    source_facts_for_census,
    source_facts_for_domain,
    source_facts_for_fred,
    source_facts_for_geocoding,
    source_facts_for_news,
    source_facts_for_wikipedia,
)
from app.schemas.lead import Enrichment, LeadCreate, SourceFact


class PublicDataToolOutput(BaseModel):
    """Normalized JSON returned from public-data research tools."""

    status: Literal["ok", "not_found", "unavailable"]
    summary: str
    source_facts: list[SourceFact] = Field(default_factory=list)
    warning: str | None = None


async def enrich_lead_with_public_data(
    *,
    public_data_client: PublicDataClient,
    lead: LeadCreate,
) -> Enrichment:
    return await public_data_client.enrich(lead)


def create_geocoding_tool() -> StructuredTool:
    async def _geocode_property_address(
        street: Annotated[str, Field(description="Property street address.")],
        city: Annotated[str, Field(description="Property city.")],
        state: Annotated[str, Field(description="Property state.")],
        public_data_client: Annotated[object, InjectedToolArg],
        country: Annotated[str, Field(description="Property country.")] = "US",
    ) -> str:
        """Resolve a property address to coordinates and place context."""
        try:
            result = await public_data_client.geocode_address(
                street=street,
                city=city,
                state=state,
                country=country,
            )
        except Exception:  # noqa: BLE001
            return _unavailable("Geocoding data is unavailable.")
        facts = source_facts_for_geocoding(result)
        if not facts or result is None:
            return _not_found("No geocoding result found for the property address.")
        return _ok(
            f"Resolved property near {result.city or city}, {result.state or state}.",
            facts,
        )

    return StructuredTool.from_function(
        coroutine=_geocode_property_address,
        name="geocode_property_address",
        description=(
            "Resolve a property address through the geocoding public API. Use when "
            "market or address context needs verification before drafting."
        ),
    )


def create_census_tool() -> StructuredTool:
    async def _fetch_census_market_demographics(
        city: Annotated[str, Field(description="Market city.")],
        state: Annotated[str, Field(description="Market state.")],
        public_data_client: Annotated[object, InjectedToolArg],
    ) -> str:
        """Fetch renter, rent, and household-count data for a market."""
        try:
            result = await public_data_client.census_market_snapshot(
                city=city,
                state=state,
            )
        except Exception:  # noqa: BLE001
            return _unavailable("Census ACS market demographics are unavailable.")
        facts = source_facts_for_census(result)
        if not facts:
            return _not_found("No Census ACS market demographics found.")
        return _ok("Found Census ACS market demographics.", facts)

    return StructuredTool.from_function(
        coroutine=_fetch_census_market_demographics,
        name="fetch_census_market_demographics",
        description=(
            "Fetch Census ACS renter share, median rent, and household count for "
            "the lead market."
        ),
    )


def create_fred_tool() -> StructuredTool:
    async def _fetch_fred_market_economics(
        state: Annotated[str, Field(description="State or state abbreviation.")],
        public_data_client: Annotated[object, InjectedToolArg],
    ) -> str:
        """Fetch FRED rent-growth and labor-market signals."""
        try:
            result = await public_data_client.fred_snapshot(state=state)
        except Exception:  # noqa: BLE001
            return _unavailable("FRED economic data is unavailable.")
        facts = source_facts_for_fred(result)
        if not facts:
            return _not_found("No FRED economic context found.")
        return _ok("Found FRED economic context.", facts)

    return StructuredTool.from_function(
        coroutine=_fetch_fred_market_economics,
        name="fetch_fred_market_economics",
        description=(
            "Fetch FRED rent-growth and unemployment signals for the lead state. "
            "Only use when economic context would improve the draft."
        ),
    )


def create_news_tool() -> StructuredTool:
    async def _lookup_news_company_trigger(
        company: Annotated[str, Field(description="Company or operator name.")],
        public_data_client: Annotated[object, InjectedToolArg],
    ) -> str:
        """Look up a recent company trigger event from the news API."""
        try:
            result = await public_data_client.news_recent_trigger(company=company)
        except Exception:  # noqa: BLE001
            return _unavailable("Company trigger news is unavailable.")
        facts = source_facts_for_news(result)
        if not facts:
            return _not_found("No recent company trigger found.")
        return _ok("Found a recent company trigger.", facts)

    return StructuredTool.from_function(
        coroutine=_lookup_news_company_trigger,
        name="lookup_news_company_trigger",
        description=(
            "Look up one recent company trigger event. Use only if a recent event "
            "would support outreach personalization."
        ),
    )


def create_wikipedia_tool() -> StructuredTool:
    async def _lookup_wikipedia_company_background(
        company: Annotated[str, Field(description="Company or operator name.")],
        public_data_client: Annotated[object, InjectedToolArg],
    ) -> str:
        """Look up concise company background from Wikipedia search."""
        try:
            result = await public_data_client.wikipedia_company_snapshot(
                company=company,
            )
        except Exception:  # noqa: BLE001
            return _unavailable("Company background data is unavailable.")
        facts = source_facts_for_wikipedia(result)
        if not facts:
            return _not_found("No company background found.")
        return _ok("Found company background context.", facts)

    return StructuredTool.from_function(
        coroutine=_lookup_wikipedia_company_background,
        name="lookup_wikipedia_company_background",
        description=(
            "Look up concise company background from Wikipedia search. Use only "
            "for cited background context, not score or gate changes."
        ),
    )


def create_domain_tool() -> StructuredTool:
    async def _validate_email_domain_mx(
        domain: Annotated[
            str,
            Field(description="Email domain only, not a full email address."),
        ],
        public_data_client: Annotated[object, InjectedToolArg],
    ) -> str:
        """Validate whether an email domain has MX records."""
        try:
            result = await public_data_client.domain_snapshot_for_domain(
                domain=domain,
            )
        except Exception:  # noqa: BLE001
            return _unavailable("Domain validation is unavailable.")
        facts = source_facts_for_domain(result)
        if not facts:
            return _not_found("No domain validation result found.")
        return _ok("Validated email domain MX records.", facts)

    return StructuredTool.from_function(
        coroutine=_validate_email_domain_mx,
        name="validate_email_domain_mx",
        description=(
            "Validate whether a domain has MX records. The input must be a domain, "
            "not a full email address."
        ),
    )


def _ok(summary: str, source_facts: list[SourceFact]) -> str:
    return PublicDataToolOutput(
        status="ok",
        summary=summary,
        source_facts=source_facts,
    ).model_dump_json()


def _not_found(summary: str) -> str:
    return PublicDataToolOutput(
        status="not_found",
        summary=summary,
    ).model_dump_json()


def _unavailable(warning: str) -> str:
    return PublicDataToolOutput(
        status="unavailable",
        summary=warning,
        warning=warning,
    ).model_dump_json()
