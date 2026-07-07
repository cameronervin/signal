"""Hard-gate checks for Signal lead qualification."""

from app.schemas.lead import Enrichment, GateResult, LeadCreate

PERSONAL_EMAIL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "icloud.com",
    "aol.com",
    "personal.example",
}


def evaluate_gates(lead: LeadCreate, enrichment: Enrichment) -> GateResult:
    failures: list[str] = []
    warnings: list[str] = []
    domain = lead.email.split("@")[-1].lower()

    if domain in PERSONAL_EMAIL_DOMAINS:
        failures.append("personal email domain")
    if lead.country.upper() not in {"US", "USA", "UNITED STATES"}:
        failures.append("non-US property")
    if not enrichment.market:
        failures.append("address did not resolve")
    if _source_value(enrichment, "Corporate domain MX") == "No MX records found":
        failures.append("email domain has no MX records")
    if _company_unresolved(enrichment):
        failures.append("company could not resolve")
    if (enrichment.company_units or 0) < 10000:
        warnings.append("sub-scale portfolio")
    warnings.extend(enrichment.provider_warnings)

    return GateResult(
        status="failed" if failures else "passed",
        failures=failures,
        warnings=warnings,
    )


def _source_value(enrichment: Enrichment, label: str) -> str | None:
    for source in enrichment.sources:
        if source.label == label:
            return source.value
    return None


def _company_unresolved(enrichment: Enrichment) -> bool:
    if enrichment.company_units is None:
        return True
    for source in enrichment.sources:
        if source.label not in {"Company background", "Company resolution"}:
            continue
        value = source.value.lower()
        if "unresolved" in value or "not found" in value:
            return True
    return False
