from dataclasses import dataclass

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

TIER_THRESHOLDS = {
    "A": 75,
    "B": 50,
}

BONUS_POINTS = {
    "recent_trigger": 10,
    "related_context": 10,
}

SENIORITY_POINTS: dict[str, int] = {
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

ASSET_TYPE_POINTS = {
    "multifamily": 10,
    "student": 10,
    "sfr": 10,
    "unclear": 4,
    "commercial": 2,
}


@dataclass(frozen=True)
class Bucket:
    threshold: float
    points: int


@dataclass(frozen=True)
class RubricComponent:
    name: str
    max_points: int
    rationale: str
    source_refs: tuple[str, ...] = ()


COMPANY_FIT_COMPONENTS = {
    "portfolio_scale": RubricComponent(
        name="portfolio_scale",
        max_points=25,
        rationale="Company unit estimate indicates portfolio scale.",
        source_refs=("Company units",),
    ),
    "contact_seniority": RubricComponent(
        name="contact_seniority",
        max_points=15,
        rationale="Contact role suggests buying or evaluation influence.",
    ),
    "asset_type_fit": RubricComponent(
        name="asset_type_fit",
        max_points=10,
        rationale="Property and company signals fit the v1 multifamily focus.",
        source_refs=("Asset type fit",),
    ),
    "company_momentum": RubricComponent(
        name="company_momentum",
        max_points=10,
        rationale="Recent trigger or fallback company context supports urgency.",
        source_refs=("Trigger event",),
    ),
}

MARKET_OPPORTUNITY_COMPONENTS = {
    "renter_share": RubricComponent(
        name="renter_share",
        max_points=12,
        rationale="Higher renter share increases market opportunity.",
        source_refs=("Renter share",),
    ),
    "rent_level_trend": RubricComponent(
        name="rent_level_trend",
        max_points=10,
        rationale="Rent growth supports active leasing-market pressure.",
        source_refs=("Rent growth",),
    ),
    "population_household_growth": RubricComponent(
        name="population_household_growth",
        max_points=8,
        rationale="Household growth contributes to demand signal.",
        source_refs=("Household growth",),
    ),
    "labor_market_tightness": RubricComponent(
        name="labor_market_tightness",
        max_points=5,
        rationale="Lower unemployment supports leasing demand stability.",
        source_refs=("Labor market",),
    ),
    "walkability_density": RubricComponent(
        name="walkability_density",
        max_points=5,
        rationale="Local walkability or density indicates market fit.",
        source_refs=("Walkability",),
    ),
}

BONUS_COMPONENTS = {
    "recent_trigger_bonus": RubricComponent(
        name="recent_trigger_bonus",
        max_points=10,
        rationale="Recent trigger adds a bounded urgency bonus.",
        source_refs=("Trigger event",),
    ),
    "related_context_bonus": RubricComponent(
        name="related_context_bonus",
        max_points=10,
        rationale="Related inbound context adds a bounded urgency bonus.",
    ),
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
    *,
    related_context_count: int = 0,
) -> ScoreBreakdown:
    if gates.status == "failed":
        return ScoreBreakdown(
            total=0,
            tier="C",
            company_fit=0,
            market_opportunity=0,
            multipliers=[],
            why_line=f"C-tier: gate failed because {', '.join(gates.failures)}.",
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
    asset_fit = _asset_type_points(enrichment.asset_type_fit)
    momentum = 10 if enrichment.recent_trigger else 4
    company_fit = min(60, portfolio + seniority + asset_fit + momentum)

    renter = _bucket(
        enrichment.renter_share or 0,
        [Bucket(0.6, 12), Bucket(0.5, 9), Bucket(0.4, 6)],
        3,
    )
    rent = _bucket(
        (enrichment.rent_growth_yoy or 0) / 100,
        [Bucket(0.08, 10), Bucket(0.05, 8), Bucket(0.02, 5)],
        2,
    )
    growth = _bucket(
        (enrichment.household_growth or 0) / 100,
        [Bucket(0.04, 8), Bucket(0.025, 6), Bucket(0.01, 4)],
        1,
    )
    labor = _bucket(
        1 - ((enrichment.unemployment_rate or 6) / 10),
        [Bucket(0.67, 5), Bucket(0.55, 3)],
        1,
    )
    density = _bucket(
        float(enrichment.walkability_score or 0),
        [Bucket(70, 5), Bucket(55, 3), Bucket(40, 2)],
        1,
    )
    market = min(40, renter + rent + growth + labor + density)

    recent_bonus = BONUS_POINTS["recent_trigger"] if enrichment.recent_trigger else 0
    related_bonus = (
        BONUS_POINTS["related_context"] if related_context_count > 0 else 0
    )
    total = min(100, company_fit + market + recent_bonus + related_bonus)
    tier = _tier(total)
    why_line = _why_line(
        tier=tier,
        enrichment=enrichment,
        portfolio_points=portfolio,
        seniority_points=seniority,
        market_points=market,
        recent_bonus=recent_bonus,
        related_bonus=related_bonus,
    )
    multipliers = []
    if recent_bonus:
        multipliers.append(f"recent_trigger:+{recent_bonus}")
    if related_bonus:
        multipliers.append(f"related_context:+{related_bonus}")
    if not multipliers:
        multipliers.append("no_bonus")

    return ScoreBreakdown(
        total=total,
        tier=tier,
        company_fit=company_fit,
        market_opportunity=market,
        multipliers=multipliers,
        why_line=why_line,
        components=[
            _component("portfolio_scale", portfolio),
            _component("contact_seniority", seniority),
            _component("asset_type_fit", asset_fit),
            _component("company_momentum", momentum),
            _component("renter_share", renter),
            _component("rent_level_trend", rent),
            _component("population_household_growth", growth),
            _component("labor_market_tightness", labor),
            _component("walkability_density", density),
            _component("recent_trigger_bonus", recent_bonus),
            _component("related_context_bonus", related_bonus),
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


def _asset_type_points(asset_type: str | None) -> int:
    if asset_type is None:
        return ASSET_TYPE_POINTS["unclear"]
    return ASSET_TYPE_POINTS.get(asset_type, ASSET_TYPE_POINTS["unclear"])


def _bucket(value: float, thresholds: list[Bucket], fallback: int) -> int:
    for bucket in thresholds:
        if value >= bucket.threshold:
            return bucket.points
    return fallback


def _tier(score: int) -> Tier:
    if score >= TIER_THRESHOLDS["A"]:
        return "A"
    if score >= TIER_THRESHOLDS["B"]:
        return "B"
    return "C"


def _component(name: str, points: int) -> ScoreComponent:
    config = (
        COMPANY_FIT_COMPONENTS.get(name)
        or MARKET_OPPORTUNITY_COMPONENTS.get(name)
        or BONUS_COMPONENTS[name]
    )
    return ScoreComponent(
        name=config.name,
        points=min(points, config.max_points),
        rationale=config.rationale,
        source_refs=list(config.source_refs),
    )


def _why_line(
    *,
    tier: Tier,
    enrichment: Enrichment,
    portfolio_points: int,
    seniority_points: int,
    market_points: int,
    recent_bonus: int,
    related_bonus: int,
) -> str:
    reasons = []
    if portfolio_points >= 21:
        reasons.append("large portfolio")
    if seniority_points >= 12:
        reasons.append("senior contact")
    if enrichment.renter_share and enrichment.renter_share >= 0.6:
        reasons.append("high renter share")
    if enrichment.rent_growth_yoy and enrichment.rent_growth_yoy >= 5:
        reasons.append(f"{enrichment.rent_growth_yoy:.1f}% rent growth")
    if recent_bonus:
        reasons.append("recent trigger event")
    if related_bonus:
        reasons.append("related inbound context")
    if not recent_bonus:
        reasons.append("no recent trigger found")
    if tier == "C" and market_points < 20:
        reasons.append("weaker market signal")
    return f"{tier}-tier: {', '.join(reasons)}."
