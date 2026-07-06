from datetime import UTC, datetime

from app.schemas.lead import Enrichment, SourceFact


def demo_enrichment(company: str, city: str, state: str) -> Enrichment:
    retrieved_at = datetime.now(UTC)
    market = f"{city}, {state}"
    company_units = _company_units(company)
    rent_growth = 8.1 if city.lower() in {"austin", "charlotte"} else 3.4
    renter_share = 0.61 if city.lower() in {"austin", "arlington"} else 0.48
    trigger = (
        f"{company} announced regional portfolio expansion"
        if company_units >= 50000
        else None
    )
    return Enrichment(
        market=market,
        coordinates=(30.2672, -97.7431) if city.lower() == "austin" else None,
        geo_confidence="high" if city.lower() == "austin" else "medium",
        census_geo_id=f"fixture-{city.lower()}-{state.lower()}",
        renter_share=renter_share,
        median_rent=1840,
        rent_growth_yoy=rent_growth,
        household_growth=4.4,
        unemployment_rate=3.2,
        walkability_score=72 if city.lower() == "austin" else 58,
        company_units=company_units,
        asset_type_fit="multifamily",
        recent_trigger=trigger,
        domain_status="corporate",
        sources=[
            SourceFact(
                source="Census ACS",
                label="Renter share",
                value=f"{renter_share:.0%}",
                retrieved_at=retrieved_at,
                confidence="high",
            ),
            SourceFact(
                source="FRED",
                label="Rent growth",
                value=f"{rent_growth:.1f}% YoY",
                retrieved_at=retrieved_at,
                confidence="medium",
            ),
            SourceFact(
                source="News",
                label="Trigger event",
                value=trigger or "No recent trigger found",
                retrieved_at=retrieved_at,
                confidence="fallback" if trigger is None else "medium",
            ),
            SourceFact(
                source="Fixture company context",
                label="Company units",
                value=f"{company_units:,}",
                retrieved_at=retrieved_at,
                confidence="fallback",
            ),
        ],
    )


def _company_units(company: str) -> int:
    normalized = company.lower()
    if any(token in normalized for token in ("residential", "living", "property")):
        return 85000
    if any(token in normalized for token in ("homes", "communities")):
        return 42000
    return 12000
