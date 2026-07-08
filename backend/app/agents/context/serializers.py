"""Serialize deterministic Signal state into bounded model context."""

from __future__ import annotations

from app.schemas.lead import (
    Enrichment,
    GateResult,
    LeadCreate,
    ScoreBreakdown,
    SourceFact,
)

OUTREACH_FIELD_DESCRIPTIONS = {
    "lead": (
        "Inbound lead input supplied by a sales rep workflow: contact, company, "
        "role, masked email domain, and the multifamily property location."
    ),
    "gates": (
        "Hard qualification checks that decide whether outreach should be "
        "suppressed before a rep spends time on the lead."
    ),
    "score": (
        "Server-generated lead scoring output for prioritization, including "
        "tier, total score, component points, and the why-line."
    ),
    "talking_points": (
        "Sales insights that convert public API enrichment into rep-ready "
        "angles for leasing operations, follow-up urgency, and draft outreach."
    ),
    "enrichment": (
        "Normalized public API context about the property market, company, "
        "economic signals, and trigger evidence."
    ),
    "source_facts": (
        "Citable public-data facts that can support personalization claims in "
        "a review-ready draft email."
    ),
}


def build_outreach_context(
    *,
    lead: LeadCreate,
    gates: GateResult,
    enrichment: Enrichment,
    score: ScoreBreakdown,
    talking_points: list[str],
) -> dict[str, object]:
    """Build the deterministic context pack for outreach drafting."""
    domain = lead.email.split("@")[-1].lower()
    return {
        "field_descriptions": OUTREACH_FIELD_DESCRIPTIONS,
        "lead": {
            "contact_name": lead.contact_name,
            "company": lead.company,
            "role": lead.role,
            "email": f"***@{domain}",
            "email_domain": domain,
            "property_address": lead.property_address,
            "city": lead.city,
            "state": lead.state,
            "country": lead.country,
        },
        "gates": gates.model_dump(mode="json"),
        "score": score.model_dump(mode="json"),
        "talking_points": talking_points,
        "enrichment": {
            "market": enrichment.market,
            "coordinates": enrichment.coordinates,
            "renter_share": enrichment.renter_share,
            "median_rent": enrichment.median_rent,
            "rent_growth_yoy": enrichment.rent_growth_yoy,
            "household_growth": enrichment.household_growth,
            "unemployment_rate": enrichment.unemployment_rate,
            "company_units": enrichment.company_units,
            "recent_trigger": enrichment.recent_trigger,
            "provider_warnings": enrichment.provider_warnings,
        },
        "source_facts": [
            _source_fact_payload(source) for source in enrichment.sources
        ],
    }


def _source_fact_payload(source: SourceFact) -> dict[str, str | None]:
    return source.model_dump(mode="json")
