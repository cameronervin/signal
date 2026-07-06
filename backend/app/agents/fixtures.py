from app.schemas.lead import Enrichment, SourceFact


def demo_enrichment(company: str, city: str, state: str) -> Enrichment:
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
        renter_share=renter_share,
        median_rent=1840,
        rent_growth_yoy=rent_growth,
        household_growth=4.4,
        unemployment_rate=3.2,
        company_units=company_units,
        recent_trigger=trigger,
        sources=[
            SourceFact(
                source="Census ACS",
                label="Renter share",
                value=f"{renter_share:.0%}",
            ),
            SourceFact(
                source="FRED",
                label="Rent growth",
                value=f"{rent_growth:.1f}% YoY",
            ),
            SourceFact(
                source="News",
                label="Trigger event",
                value=trigger or "No recent trigger found",
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
