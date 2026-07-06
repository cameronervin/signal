from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings
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


@dataclass(frozen=True)
class ScoringRubric:
    tier_thresholds: dict[Tier, int]
    gate_failed_score: int
    bonuses: dict[str, int]
    seniority_points: dict[str, int]
    asset_type_points: dict[str, int]
    portfolio_buckets: tuple[Bucket, ...]
    portfolio_fallback_points: int
    market_buckets: dict[str, tuple[Bucket, ...]]
    market_fallback_points: dict[str, int]
    components: dict[str, RubricComponent]


def evaluate_gates(
    lead: LeadCreate,
    enrichment: Enrichment,
    warnings: list[str] | None = None,
) -> GateResult:
    failures: list[str] = []
    gate_warnings: list[str] = [*(warnings or [])]

    if lead.country.upper() not in {"US", "USA", "UNITED STATES"}:
        failures.append("non-US property")
    if (
        not enrichment.market
        or enrichment.coordinates is None
        or enrichment.geo_confidence is None
    ):
        failures.append("address did not resolve")
    if enrichment.domain_status != "corporate":
        failures.append("corporate domain not verified")
    if enrichment.company_units is None or enrichment.asset_type_fit == "unclear":
        failures.append("company plausibility unresolved")
    elif enrichment.company_units < 10000:
        gate_warnings.append("sub-scale portfolio")

    return GateResult(
        status="failed" if failures else "passed",
        failures=failures,
        warnings=gate_warnings,
    )


def score_lead(
    lead: LeadCreate,
    gates: GateResult,
    enrichment: Enrichment,
    *,
    related_context_count: int = 0,
    rubric: ScoringRubric | None = None,
) -> ScoreBreakdown:
    active_rubric = rubric or load_default_scoring_rubric()
    if gates.status == "failed":
        return ScoreBreakdown(
            total=active_rubric.gate_failed_score,
            tier="C",
            company_fit=0,
            market_opportunity=0,
            multipliers=[],
            why_line=f"C-tier: gate failed because {', '.join(gates.failures)}.",
            components=[
                ScoreComponent(
                    name="gates",
                    points=active_rubric.gate_failed_score,
                    rationale="Hard gate failure forces C-tier and suppresses draft.",
                )
            ],
        )

    portfolio = _portfolio_points(enrichment.company_units or 0, active_rubric)
    seniority = _seniority_points(lead.role or "", active_rubric)
    asset_fit = _asset_type_points(enrichment.asset_type_fit, active_rubric)
    momentum = (
        active_rubric.components["company_momentum"].max_points
        if enrichment.recent_trigger
        else 4
    )
    company_fit = min(60, portfolio + seniority + asset_fit + momentum)

    renter = _bucket(
        enrichment.renter_share or 0,
        active_rubric.market_buckets["renter_share"],
        active_rubric.market_fallback_points["renter_share"],
    )
    rent = _bucket(
        (enrichment.rent_growth_yoy or 0) / 100,
        active_rubric.market_buckets["rent_level_trend"],
        active_rubric.market_fallback_points["rent_level_trend"],
    )
    growth = _bucket(
        (enrichment.household_growth or 0) / 100,
        active_rubric.market_buckets["population_household_growth"],
        active_rubric.market_fallback_points["population_household_growth"],
    )
    labor = _bucket(
        1 - ((enrichment.unemployment_rate or 6) / 10),
        active_rubric.market_buckets["labor_market_tightness"],
        active_rubric.market_fallback_points["labor_market_tightness"],
    )
    density = _bucket(
        float(enrichment.walkability_score or 0),
        active_rubric.market_buckets["walkability_density"],
        active_rubric.market_fallback_points["walkability_density"],
    )
    market = min(40, renter + rent + growth + labor + density)

    recent_bonus = (
        active_rubric.bonuses["recent_trigger"] if enrichment.recent_trigger else 0
    )
    related_bonus = (
        active_rubric.bonuses["related_context"] if related_context_count > 0 else 0
    )
    total = min(100, company_fit + market + recent_bonus + related_bonus)
    tier = _tier(total, active_rubric)
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
            _component("portfolio_scale", portfolio, active_rubric),
            _component("contact_seniority", seniority, active_rubric),
            _component("asset_type_fit", asset_fit, active_rubric),
            _component("company_momentum", momentum, active_rubric),
            _component("renter_share", renter, active_rubric),
            _component("rent_level_trend", rent, active_rubric),
            _component("population_household_growth", growth, active_rubric),
            _component("labor_market_tightness", labor, active_rubric),
            _component("walkability_density", density, active_rubric),
            _component("recent_trigger_bonus", recent_bonus, active_rubric),
            _component("related_context_bonus", related_bonus, active_rubric),
        ],
    )


@lru_cache
def load_default_scoring_rubric() -> ScoringRubric:
    return load_scoring_rubric(get_settings().scoring_config_path)


def load_scoring_rubric(config_path: str | Path) -> ScoringRubric:
    path = _resolve_config_path(config_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    components = {
        name: RubricComponent(
            name=name,
            max_points=int(config["max_points"]),
            rationale=str(config["rationale"]),
            source_refs=tuple(config.get("source_refs", [])),
        )
        for name, config in data["components"].items()
    }
    return ScoringRubric(
        tier_thresholds={
            "A": int(data["tier_thresholds"]["A"]),
            "B": int(data["tier_thresholds"]["B"]),
            "C": int(data["tier_thresholds"].get("C", 0)),
        },
        gate_failed_score=int(data["gate_failed_score"]),
        bonuses={key: int(value) for key, value in data["bonuses"].items()},
        seniority_points={
            key: int(value) for key, value in data["seniority_points"].items()
        },
        asset_type_points={
            key: int(value) for key, value in data["asset_type_points"].items()
        },
        portfolio_buckets=_load_buckets(data["portfolio_scale"]["buckets"]),
        portfolio_fallback_points=int(data["portfolio_scale"]["fallback_points"]),
        market_buckets={
            name: _load_buckets(config["buckets"])
            for name, config in data["market_buckets"].items()
        },
        market_fallback_points={
            name: int(config["fallback_points"])
            for name, config in data["market_buckets"].items()
        },
        components=components,
    )


def _resolve_config_path(config_path: str | Path) -> Path:
    path = Path(config_path)
    if path.is_absolute():
        return path
    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path
    backend_root = Path(__file__).resolve().parents[2]
    return backend_root / path


def _load_buckets(raw_buckets: list[dict[str, object]]) -> tuple[Bucket, ...]:
    return tuple(
        Bucket(threshold=float(bucket["threshold"]), points=int(bucket["points"]))
        for bucket in raw_buckets
    )


def _portfolio_points(units: int, rubric: ScoringRubric) -> int:
    return _bucket(units, rubric.portfolio_buckets, rubric.portfolio_fallback_points)


def _seniority_points(role: str, rubric: ScoringRubric) -> int:
    normalized = role.lower()
    for token, points in rubric.seniority_points.items():
        if token in normalized:
            return points
    return 4


def _asset_type_points(asset_type: str | None, rubric: ScoringRubric) -> int:
    if asset_type is None:
        return rubric.asset_type_points["unclear"]
    return rubric.asset_type_points.get(asset_type, rubric.asset_type_points["unclear"])


def _bucket(value: float, thresholds: tuple[Bucket, ...], fallback: int) -> int:
    for bucket in thresholds:
        if value >= bucket.threshold:
            return bucket.points
    return fallback


def _tier(score: int, rubric: ScoringRubric) -> Tier:
    if score >= rubric.tier_thresholds["A"]:
        return "A"
    if score >= rubric.tier_thresholds["B"]:
        return "B"
    return "C"


def _component(name: str, points: int, rubric: ScoringRubric) -> ScoreComponent:
    config = rubric.components[name]
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
