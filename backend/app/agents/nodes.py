from app.agents.scoring import evaluate_gates, score_lead
from app.agents.state import SignalState
from app.core.config import get_settings
from app.integrations.public_data import PublicDataClient, PublicDataClientConfig
from app.schemas.lead import DraftEmail, RelatedLead


async def deterministic_enrichment_node(state: SignalState) -> dict:
    lead = state["lead"]
    settings = get_settings()
    client = PublicDataClient(
        PublicDataClientConfig(
            use_fixtures=settings.use_fixtures,
            news_api_key=(
                settings.news_api_key.get_secret_value()
                if settings.news_api_key is not None
                else None
            ),
            fred_api_key=(
                settings.fred_api_key.get_secret_value()
                if settings.fred_api_key is not None
                else None
            ),
            timeout_seconds=settings.provider_timeout_seconds,
        )
    )
    result = await client.enrich(lead)
    enrichment = result.enrichment
    gates = evaluate_gates(lead, enrichment, result.warnings)
    flags = [*gates.failures, *gates.warnings]
    return {
        "enrichment": enrichment,
        "gates": gates,
        "flags": flags,
        "degraded_reasons": result.degraded_reasons,
        "activity_log": [
            *state.get("activity_log", []),
            *result.activity_entries,
            "deterministic_enrichment: completed",
        ],
    }


async def agent_scoring_and_drafting_node(state: SignalState) -> dict:
    lead = state["lead"]
    gates = state["gates"]
    enrichment = state["enrichment"]
    score = score_lead(lead, gates, enrichment)
    talking_points = _talking_points(enrichment)
    draft = (
        None
        if gates.status == "failed"
        else _draft_email(lead, enrichment, talking_points)
    )
    return {
        "score": score,
        "talking_points": talking_points,
        "draft": draft,
        "activity_log": [
            *state.get("activity_log", []),
            "agent_scoring_and_drafting: completed",
        ],
    }


async def knowledge_graph_builder_node(state: SignalState) -> dict:
    lead = state["lead"]
    related = [
        RelatedLead(
            lead_id="demo-related-001",
            label=f"{lead.company} related inbound",
            reason="Same company appeared in fixture history",
            relationship_type="company",
            score_impact="Related context is available for SDR review.",
        )
    ]
    return {
        "related_leads": related,
        "activity_log": [
            *state.get("activity_log", []),
            "knowledge_graph_builder: completed",
            "human_review: awaiting approval",
        ],
    }


def _talking_points(enrichment) -> list[str]:
    points = []
    if enrichment.renter_share is not None:
        points.append(
            f"{enrichment.market} renter share is {enrichment.renter_share:.0%}."
        )
    if enrichment.rent_growth_yoy is not None:
        points.append(
            f"Local rent growth is {enrichment.rent_growth_yoy:.1f}% year over year."
        )
    if enrichment.company_units:
        points.append(
            f"Portfolio scale signal: about {enrichment.company_units:,} units."
        )
    return points


def _draft_email(lead, enrichment, talking_points: list[str]) -> DraftEmail:
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
    return DraftEmail(
        subject=subject,
        body=body,
        talking_points=talking_points,
        sources=enrichment.sources,
        generation_mode="fallback_template",
    )
