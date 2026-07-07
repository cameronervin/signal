from app.agents.guardrails import evaluate_gates
from app.schemas.lead import Enrichment, LeadCreate, SourceFact


def _lead(**overrides: object) -> LeadCreate:
    payload = {
        "contact_name": "Sample Contact",
        "email": "lead@sampleoperator.example",
        "company": "Sample Multifamily Group",
        "role": "VP Leasing",
        "property_address": "100 Main St",
        "city": "Austin",
        "state": "TX",
        "country": "US",
    }
    payload.update(overrides)
    return LeadCreate.model_validate(payload)


def _enrichment(**overrides: object) -> Enrichment:
    payload = {
        "market": "Austin, TX",
        "company_units": 25000,
        "sources": [],
    }
    payload.update(overrides)
    return Enrichment.model_validate(payload)


def test_qualification_gates_fail_for_no_mx_source_fact() -> None:
    result = evaluate_gates(
        _lead(),
        _enrichment(
            sources=[
                SourceFact(
                    source="DNS MX",
                    label="Corporate domain MX",
                    value="No MX records found",
                )
            ]
        ),
    )

    assert result.status == "failed"
    assert "email domain has no MX records" in result.failures


def test_qualification_gates_keep_subscale_portfolio_as_warning() -> None:
    result = evaluate_gates(_lead(), _enrichment(company_units=5000))

    assert result.status == "passed"
    assert result.failures == []
    assert result.warnings == ["sub-scale portfolio"]


def test_qualification_gates_fail_for_unresolved_company() -> None:
    result = evaluate_gates(
        _lead(),
        _enrichment(
            sources=[
                SourceFact(
                    source="Company registry",
                    label="Company resolution",
                    value="Unresolved company",
                )
            ]
        ),
    )

    assert result.status == "failed"
    assert "company could not resolve" in result.failures
