from app.schemas.lead import (
    Enrichment,
    GateResult,
    LeadCreate,
    ScoreBreakdown,
    ScoreComponent,
    Tier,
)

PERSONAL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "icloud.com",
    "aol.com",
}

SENIORITY_POINTS = {
    "chief": 15,
    "cfo": 15,
    "ceo": 15,
    "coo": 15,
    "vp": 15,
    "vice president": 15,
    "director": 12,
    "regional": 10,
    "manager": 7,
}


def evaluate_gates(lead: LeadCreate, enrichment: Enrichment) -> GateResult:
    failures: list[str] = []
    warnings: list[str] = []
    domain = lead.email.split("@")[-1].lower()

    if domain in PERSONAL_DOMAINS:
        failures.append("personal email domain")
    if lead.country.upper() not in {"US", "USA", "UNITED STATES"}:
        failures.append("non-US property")
    if not enrichment.market:
        failures.append("address did not resolve")
    if (enrichment.company_units or 0) < 10000:
        warnings.append("sub-scale portfolio")

    return GateResult(
        status="failed" if failures else "passed",
        failures=failures,
        warnings=warnings,
    )


def score_lead(
    lead: LeadCreate,
    gates: GateResult,
    enrichment: Enrichment,
) -> ScoreBreakdown:
    if gates.status == "failed":
        return ScoreBreakdown(
            total=28,
            tier="C",
            company_fit=0,
            market_opportunity=0,
            multipliers=[],
            why_line=f"Gate failed: {', '.join(gates.failures)}",
            components=[
                ScoreComponent(
                    name="gates",
                    points=0,
                    rationale="Hard gate failure forces C-tier and suppresses draft.",
                )
            ],
        )

    portfolio = _portfolio_points(enrichment.company_units or 0)
    seniority = _seniority_points(lead.role or "")
    asset_fit = 10
    momentum = 10 if enrichment.recent_trigger else 4
    company_fit = min(60, portfolio + seniority + asset_fit + momentum)

    renter = _bucket(enrichment.renter_share or 0, [(0.6, 12), (0.5, 9), (0.4, 6)], 3)
    rent = _bucket(
        (enrichment.rent_growth_yoy or 0) / 100,
        [(0.08, 10), (0.05, 8), (0.02, 5)],
        2,
    )
    growth = _bucket(
        (enrichment.household_growth or 0) / 100,
        [(0.04, 8), (0.025, 6), (0.01, 4)],
        1,
    )
    labor = _bucket(
        1 - ((enrichment.unemployment_rate or 6) / 10),
        [(0.68, 5), (0.55, 3)],
        1,
    )
    density = 4
    market = min(40, renter + rent + growth + labor + density)

    bonuses = 10 if enrichment.recent_trigger else 0
    total = min(100, company_fit + market + bonuses)
    tier = _tier(total)
    why_line = _why_line(enrichment, portfolio, seniority, bonuses)
    multipliers = (
        ["recent_trigger:+10"] if enrichment.recent_trigger else ["no_multiplier"]
    )

    return ScoreBreakdown(
        total=total,
        tier=tier,
        company_fit=company_fit,
        market_opportunity=market,
        multipliers=multipliers,
        why_line=why_line,
        components=[
            ScoreComponent(
                name="portfolio_scale",
                points=portfolio,
                rationale="Company unit estimate indicates portfolio scale.",
                source_refs=["Company units"],
            ),
            ScoreComponent(
                name="seniority",
                points=seniority,
                rationale="Contact role suggests buying or evaluation influence.",
            ),
            ScoreComponent(
                name="asset_type_fit",
                points=asset_fit,
                rationale="Property and company signals fit the v1 multifamily focus.",
            ),
            ScoreComponent(
                name="momentum",
                points=momentum,
                rationale="Recent trigger or fallback market context supports urgency.",
                source_refs=["Trigger event"],
            ),
            ScoreComponent(
                name="renter_share",
                points=renter,
                rationale="Higher renter share increases market opportunity.",
                source_refs=["Renter share"],
            ),
            ScoreComponent(
                name="rent_growth",
                points=rent,
                rationale="Rent growth supports active leasing-market pressure.",
                source_refs=["Rent growth"],
            ),
            ScoreComponent(
                name="household_growth",
                points=growth,
                rationale="Household growth contributes to demand signal.",
            ),
            ScoreComponent(
                name="labor_market",
                points=labor,
                rationale="Lower unemployment supports leasing demand stability.",
            ),
            ScoreComponent(
                name="walkability_density",
                points=density,
                rationale="Fixture local-context signal indicates density fit.",
            ),
            ScoreComponent(
                name="trigger_bonus",
                points=bonuses,
                rationale="Recent trigger adds a bounded urgency bonus.",
                source_refs=["Trigger event"],
            ),
        ],
    )


def _portfolio_points(units: int) -> int:
    if units >= 75000:
        return 25
    if units >= 40000:
        return 21
    if units >= 15000:
        return 14
    return 6


def _seniority_points(role: str) -> int:
    normalized = role.lower()
    for token, points in SENIORITY_POINTS.items():
        if token in normalized:
            return points
    return 4


def _bucket(value: float, thresholds: list[tuple[float, int]], fallback: int) -> int:
    for threshold, points in thresholds:
        if value >= threshold:
            return points
    return fallback


def _tier(score: int) -> Tier:
    if score >= 75:
        return "A"
    if score >= 50:
        return "B"
    return "C"


def _why_line(
    enrichment: Enrichment,
    portfolio_points: int,
    seniority_points: int,
    bonuses: int,
) -> str:
    reasons = []
    if portfolio_points >= 21:
        reasons.append("large portfolio")
    if seniority_points >= 12:
        reasons.append("senior contact")
    if enrichment.rent_growth_yoy and enrichment.rent_growth_yoy >= 5:
        reasons.append(f"{enrichment.rent_growth_yoy:.1f}% rent growth")
    if bonuses:
        reasons.append("recent trigger event")
    return " · ".join(reasons) if reasons else "Solid fit with moderate market signal"
