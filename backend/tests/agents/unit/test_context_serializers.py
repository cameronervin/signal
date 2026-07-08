from app.agents.context import build_outreach_context
from app.agents.guardrails.qualification import evaluate_gates
from app.agents.utils.scoring import load_scoring_config, score_lead
from app.core.config import Settings
from app.infrastructure.public_data.fixtures import demo_enrichment
from app.schemas.lead import LeadCreate


def test_outreach_context_includes_use_case_field_descriptions() -> None:
    lead = LeadCreate(
        contact_name="Sample Contact",
        email="sample@operator.example",
        company="Multifamily Operator",
        role="VP Leasing",
        property_address="100 Main St",
        city="Austin",
        state="TX",
        country="US",
    )
    enrichment = demo_enrichment(lead.company, lead.city, lead.state)
    gates = evaluate_gates(lead, enrichment)
    score = score_lead(
        lead,
        gates,
        enrichment,
        config=load_scoring_config(Settings()),
    )

    context = build_outreach_context(
        lead=lead,
        gates=gates,
        enrichment=enrichment,
        score=score,
        talking_points=["Sales insight for follow-up."],
    )

    descriptions = context["field_descriptions"]
    assert isinstance(descriptions, dict)
    assert context["lead"]["email"] == "***@operator.example"
    assert "sample@" not in str(context)
    assert "lead scoring output" in descriptions["score"].lower()
    assert "sales insights" in descriptions["talking_points"].lower()
    assert "public api context" in descriptions["enrichment"].lower()
    assert "review-ready draft email" in descriptions["source_facts"].lower()
