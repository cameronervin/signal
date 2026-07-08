from app.agents.chains.outreach_drafting import _compose_instructions
from app.agents.context import build_outreach_context
from app.agents.guardrails.qualification import evaluate_gates
from app.agents.prompts.outreach import OUTREACH_DRAFT_INSTRUCTIONS
from app.agents.tools.public_data import create_census_tool
from app.agents.utils.scoring import load_scoring_config, score_lead
from app.core.config import Settings
from app.infrastructure.public_data.fixtures import demo_enrichment
from app.schemas.lead import LeadCreate


def test_outreach_prompt_has_required_structured_sections() -> None:
    for section in (
        "<role>",
        "<task>",
        "<available_data>",
        "<constraints>",
        "<tone>",
        "<email_shape>",
        "<examples>",
    ):
        assert section in OUTREACH_DRAFT_INSTRUCTIONS


def test_outreach_prompt_composition_appends_active_tool_snippets() -> None:
    instructions = _compose_instructions([create_census_tool()])

    assert instructions.startswith(OUTREACH_DRAFT_INSTRUCTIONS)
    assert "- **fetch_census_market_demographics**" in instructions
    assert "Use this for renter share" in instructions


def test_outreach_prompt_regression_for_inbound_source_grounded_cta() -> None:
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
        talking_points=["Use market context."],
    )
    prompt = OUTREACH_DRAFT_INSTRUCTIONS.lower()

    assert context["lead"]["email"] == "***@operator.example"
    assert "inbound" in prompt
    assert "lead scoring output" in prompt
    assert "sales insights" in prompt
    assert "public api" in prompt
    assert "cited public-data facts" in prompt
    assert "review-ready" in prompt
    assert "use only supplied context or returned tool source facts" in prompt
    assert "warm, direct, specific, and plainspoken" in prompt
    assert "low-friction next step" in prompt
    assert "agentic leasing platform" in prompt
    assert "do not invent company news" in prompt
    assert "roi" in prompt
    assert "do not include raw email addresses" in prompt
