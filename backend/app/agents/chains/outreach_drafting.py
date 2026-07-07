"""Deterministic outreach drafting chain for Signal lead intelligence."""

from __future__ import annotations

from typing import Any

from app.schemas.lead import DraftEmail, Enrichment, LeadCreate

OUTREACH_DRAFT_CHAIN = "outreach_draft"


class DeterministicOutreachDraftChain:
    """Small chain-shaped adapter for demo-safe draft generation."""

    async def ainvoke(
        self,
        input: dict[str, Any],
        *,
        config: dict[str, object] | None = None,
        context: object | None = None,
    ) -> DraftEmail:
        lead = input["lead"]
        enrichment = input["enrichment"]
        if not isinstance(lead, LeadCreate) or not isinstance(enrichment, Enrichment):
            raise TypeError("Signal draft chain requires LeadCreate and Enrichment")
        return _draft_email(lead, enrichment)


def create_outreach_draft_chain() -> DeterministicOutreachDraftChain:
    """Create the deterministic outreach draft chain."""
    return DeterministicOutreachDraftChain()


def _draft_email(lead: LeadCreate, enrichment: Enrichment) -> DraftEmail:
    subject = f"Improving leasing response in {lead.city}"
    trigger_sentence = (
        f"I noticed {enrichment.recent_trigger.lower()}."
        if enrichment.recent_trigger
        else f"I was looking at leasing demand signals around {enrichment.market}."
    )
    body = (
        f"Hi {lead.contact_name.split()[0]},\n\n"
        f"{trigger_sentence} Public market data also points to "
        f"{enrichment.renter_share:.0%} renter share and "
        f"{enrichment.rent_growth_yoy:.1f}% rent growth in the market.\n\n"
        "Signal flagged this as a strong fit because leasing teams can use faster "
        "response, cleaner prioritization, and better follow-up visibility when "
        "inbound demand spikes.\n\n"
        "Would it be worth comparing how your team is handling those leads today?"
    )
    return DraftEmail(subject=subject, body=body, sources=enrichment.sources)
