from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.schemas.lead import Enrichment, GateResult, LeadCreate, ScoreBreakdown, Tier


class ScoreBucket(BaseModel):
    threshold: float
    points: int


class ScoringConfig(BaseModel):
    seniority_points: dict[str, int] = Field(
        default_factory=lambda: {
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
    )
    seniority_fallback: int = 4
    portfolio_buckets: list[ScoreBucket] = Field(
        default_factory=lambda: [
            ScoreBucket(threshold=75000, points=25),
            ScoreBucket(threshold=40000, points=21),
            ScoreBucket(threshold=15000, points=14),
        ]
    )
    portfolio_fallback: int = 6
    asset_type_fit: int = 10
    momentum_with_trigger: int = 10
    momentum_without_trigger: int = 4
    renter_share_buckets: list[ScoreBucket] = Field(
        default_factory=lambda: [
            ScoreBucket(threshold=0.6, points=12),
            ScoreBucket(threshold=0.5, points=9),
            ScoreBucket(threshold=0.4, points=6),
        ]
    )
    renter_share_fallback: int = 3
    rent_growth_buckets: list[ScoreBucket] = Field(
        default_factory=lambda: [
            ScoreBucket(threshold=0.08, points=10),
            ScoreBucket(threshold=0.05, points=8),
            ScoreBucket(threshold=0.02, points=5),
        ]
    )
    rent_growth_fallback: int = 2
    household_growth_buckets: list[ScoreBucket] = Field(
        default_factory=lambda: [
            ScoreBucket(threshold=0.04, points=8),
            ScoreBucket(threshold=0.025, points=6),
            ScoreBucket(threshold=0.01, points=4),
        ]
    )
    household_growth_fallback: int = 1
    labor_market_buckets: list[ScoreBucket] = Field(
        default_factory=lambda: [
            ScoreBucket(threshold=0.68, points=5),
            ScoreBucket(threshold=0.55, points=3),
        ]
    )
    labor_market_fallback: int = 1
    walkability_density: int = 4
    trigger_bonus: int = 10
    company_fit_max: int = 60
    market_opportunity_max: int = 40
    total_max: int = 100
    tier_a_min: int = 75
    tier_b_min: int = 50
    gate_failed_score: int = 28


def score_lead(
    lead: LeadCreate,
    gates: GateResult,
    enrichment: Enrichment,
    *,
    config: ScoringConfig | None = None,
) -> ScoreBreakdown:
    scoring_config = config or load_scoring_config()
    if gates.status == "failed":
        return ScoreBreakdown(
            total=scoring_config.gate_failed_score,
            tier="C",
            company_fit=0,
            market_opportunity=0,
            bonuses=0,
            why_line=f"Gate failed: {', '.join(gates.failures)}",
            components={"gates": 0},
        )

    portfolio = _portfolio_points(enrichment.company_units or 0, scoring_config)
    seniority = _seniority_points(lead.role or "", scoring_config)
    asset_fit = scoring_config.asset_type_fit
    momentum = (
        scoring_config.momentum_with_trigger
        if enrichment.recent_trigger
        else scoring_config.momentum_without_trigger
    )
    company_fit = min(
        scoring_config.company_fit_max,
        portfolio + seniority + asset_fit + momentum,
    )

    renter = _bucket(
        enrichment.renter_share or 0,
        scoring_config.renter_share_buckets,
        scoring_config.renter_share_fallback,
    )
    rent = _bucket(
        (enrichment.rent_growth_yoy or 0) / 100,
        scoring_config.rent_growth_buckets,
        scoring_config.rent_growth_fallback,
    )
    growth = _bucket(
        (enrichment.household_growth or 0) / 100,
        scoring_config.household_growth_buckets,
        scoring_config.household_growth_fallback,
    )
    labor = _bucket(
        1 - ((enrichment.unemployment_rate or 6) / 10),
        scoring_config.labor_market_buckets,
        scoring_config.labor_market_fallback,
    )
    density = scoring_config.walkability_density
    market = min(
        scoring_config.market_opportunity_max,
        renter + rent + growth + labor + density,
    )

    bonuses = scoring_config.trigger_bonus if enrichment.recent_trigger else 0
    total = min(scoring_config.total_max, company_fit + market + bonuses)
    tier = _tier(total, scoring_config)
    why_line = _why_line(enrichment, portfolio, seniority, bonuses)

    return ScoreBreakdown(
        total=total,
        tier=tier,
        company_fit=company_fit,
        market_opportunity=market,
        bonuses=bonuses,
        why_line=why_line,
        components={
            "portfolio_scale": portfolio,
            "seniority": seniority,
            "asset_type_fit": asset_fit,
            "momentum": momentum,
            "renter_share": renter,
            "rent_growth": rent,
            "household_growth": growth,
            "labor_market": labor,
            "walkability_density": density,
            "trigger_bonus": bonuses,
        },
    )


def load_scoring_config(settings: Settings | None = None) -> ScoringConfig:
    app_settings = settings or get_settings()
    return _load_scoring_config(app_settings.scoring_config_path or None)


@lru_cache
def _load_scoring_config(config_path: str | None) -> ScoringConfig:
    if config_path is None:
        return ScoringConfig()
    return ScoringConfig.model_validate_json(Path(config_path).read_text())


def clear_scoring_config_cache() -> None:
    _load_scoring_config.cache_clear()


def _portfolio_points(units: int, config: ScoringConfig) -> int:
    for bucket in config.portfolio_buckets:
        if units >= bucket.threshold:
            return bucket.points
    return config.portfolio_fallback


def _seniority_points(role: str, config: ScoringConfig) -> int:
    normalized = role.lower()
    for token, points in config.seniority_points.items():
        if token in normalized:
            return points
    return config.seniority_fallback


def _bucket(
    value: float,
    thresholds: list[ScoreBucket],
    fallback: int,
) -> int:
    for bucket in thresholds:
        if value >= bucket.threshold:
            return bucket.points
    return fallback


def _tier(score: int, config: ScoringConfig) -> Tier:
    if score >= config.tier_a_min:
        return "A"
    if score >= config.tier_b_min:
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
