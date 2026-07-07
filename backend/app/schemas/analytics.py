from pydantic import BaseModel, Field


class MarketSummary(BaseModel):
    market: str
    lead_count: int


class AnalyticsSummaryResponse(BaseModel):
    total_leads: int
    tier_distribution: dict[str, int] = Field(
        default_factory=lambda: {"A": 0, "B": 0, "C": 0}
    )
    awaiting_review_count: int
    gate_failed_count: int
    average_score: float
    top_markets: list[MarketSummary] = Field(default_factory=list)
