from app.agents.utils.scoring import score_lead
from app.infrastructure.public_data.fixtures import demo_enrichment
from app.schemas.lead import DraftEmail, GateResult, LeadCreate
from app.services.agent_run_builder import build_agent_run_response
from app.services.lead_response_builder import build_lead_response


def _lead() -> LeadCreate:
    return LeadCreate(
        contact_name="Sample Contact",
        email="lead@sampleoperator.example",
        company="Sample Multifamily Group",
        role="VP Leasing",
        property_address="100 Main St",
        city="Austin",
        state="TX",
        country="US",
    )


def test_lead_response_builder_defaults_optional_graph_outputs() -> None:
    lead = _lead()
    gates = GateResult(status="passed")
    enrichment = demo_enrichment(lead.company, lead.city, lead.state)
    response = build_lead_response(
        lead_id="lead_test",
        run_id="run_test",
        lead=lead,
        result={
            "lead_id": "lead_test",
            "run_id": "run_test",
            "lead": lead,
            "gates": gates,
            "enrichment": enrichment,
            "score": score_lead(lead, gates, enrichment),
        },
    )

    assert response.id == "lead_test"
    assert response.run_id == "run_test"
    assert response.talking_points == []
    assert response.flags == []
    assert response.related_leads == []


def test_agent_run_builder_preserves_human_review_gate() -> None:
    lead = _lead()
    gates = GateResult(status="passed")
    enrichment = demo_enrichment(lead.company, lead.city, lead.state)
    response = build_lead_response(
        lead_id="lead_test",
        run_id="run_test",
        lead=lead,
        result={
            "lead_id": "lead_test",
            "run_id": "run_test",
            "lead": lead,
            "gates": gates,
            "enrichment": enrichment,
            "score": score_lead(lead, gates, enrichment),
            "draft": DraftEmail(
                subject="Improving leasing response in Austin",
                body="Model-backed draft",
                sources=enrichment.sources,
            ),
        },
    )

    run = build_agent_run_response(
        lead=response,
        activity_log=["deterministic_enrichment: completed"],
    )

    assert run.status == "awaiting_review"
    assert run.trigger == "api_insert"
    assert run.current_stage == "human_review"
    assert run.steps[-1].name == "Human review"
    assert run.steps[-1].status == "pending"


def test_agent_run_builder_marks_model_drafting_failure() -> None:
    lead = _lead()
    gates = GateResult(status="passed")
    enrichment = demo_enrichment(lead.company, lead.city, lead.state)
    response = build_lead_response(
        lead_id="lead_test",
        run_id="run_test",
        lead=lead,
        result={
            "lead_id": "lead_test",
            "run_id": "run_test",
            "lead": lead,
            "gates": gates,
            "enrichment": enrichment,
            "score": score_lead(lead, gates, enrichment),
            "draft": None,
        },
    )

    run = build_agent_run_response(
        lead=response,
        activity_log=["agent_research_and_drafting: model drafting failed"],
    )

    assert run.status == "failed"
    assert run.current_stage == "model_drafting_failed"
    assert run.steps[1].name == "Deterministic scoring"
    assert run.steps[1].status == "done"
    assert run.steps[2].name == "Agent research and drafting"
    assert run.steps[2].status == "failed"
    assert run.steps[-1].status == "skipped"


def test_agent_run_builder_marks_gate_failed_lead_completed() -> None:
    lead = _lead()
    gates = GateResult(status="failed", failures=["personal email domain"])
    enrichment = demo_enrichment(lead.company, lead.city, lead.state)
    response = build_lead_response(
        lead_id="lead_test",
        run_id="run_test",
        lead=lead,
        result={
            "lead_id": "lead_test",
            "run_id": "run_test",
            "lead": lead,
            "gates": gates,
            "enrichment": enrichment,
            "score": score_lead(lead, gates, enrichment),
            "draft": None,
        },
    )

    run = build_agent_run_response(lead=response, activity_log=[])

    assert run.status == "completed"
    assert run.current_stage == "gate_failed"
    assert run.steps[1].status == "done"
    assert run.steps[2].status == "skipped"
    assert run.steps[-1].status == "skipped"
