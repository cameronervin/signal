from datetime import UTC, datetime

from pydantic import BaseModel

from app.schemas.lead import Enrichment, LeadCreate, SourceFact


class DemoSeedLead(BaseModel):
    handle: str
    lead_id: str
    run_id: str
    input: LeadCreate


def demo_seed_leads() -> list[DemoSeedLead]:
    return [
        DemoSeedLead(
            handle="a_tier",
            lead_id="seed_a_tier",
            run_id="seed_run_a_tier",
            input=LeadCreate(
                contact_name="Demo Contact",
                email="contact@operator.example",
                company="National Property Operator",
                role="VP Leasing",
                property_address="100 Market St",
                city="Austin",
                state="TX",
                country="US",
                source="demo_seed",
            ),
        ),
        DemoSeedLead(
            handle="b_tier",
            lead_id="seed_b_tier",
            run_id="seed_run_b_tier",
            input=LeadCreate(
                contact_name="Demo Contact",
                email="contact@operator.example",
                company="Regional Communities Operator",
                role="Property Manager",
                property_address="200 Market St",
                city="Dallas",
                state="TX",
                country="US",
                source="demo_seed",
            ),
        ),
        DemoSeedLead(
            handle="c_tier",
            lead_id="seed_c_tier",
            run_id="seed_run_c_tier",
            input=LeadCreate(
                contact_name="Demo Contact",
                email="contact@operator.example",
                company="Local Portfolio Group",
                role="Leasing Associate",
                property_address="300 Market St",
                city="Boise",
                state="ID",
                country="US",
                source="demo_seed",
            ),
        ),
        DemoSeedLead(
            handle="warning_only",
            lead_id="seed_warning_only",
            run_id="seed_run_warning_only",
            input=LeadCreate(
                contact_name="Demo Contact",
                email="contact@operator.example",
                company="Local Portfolio Group",
                role="Regional Director",
                property_address="400 Market St",
                city="Austin",
                state="TX",
                country="US",
                source="demo_seed",
            ),
        ),
        DemoSeedLead(
            handle="missing_trigger",
            lead_id="seed_missing_trigger",
            run_id="seed_run_missing_trigger",
            input=LeadCreate(
                contact_name="Demo Contact",
                email="contact@operator.example",
                company="Neighborhood Housing Group",
                role="Regional Director",
                property_address="500 Market St",
                city="Dallas",
                state="TX",
                country="US",
                source="demo_seed",
            ),
        ),
        DemoSeedLead(
            handle="hard_gate_failed",
            lead_id="seed_hard_gate_failed",
            run_id="seed_run_hard_gate_failed",
            input=LeadCreate(
                contact_name="Demo Contact",
                email="contact@operator.example",
                company="Unverified Housing Group",
                role="Property Manager",
                property_address="600 Market St",
                city="Toronto",
                state="ON",
                country="CA",
                source="demo_seed",
            ),
        ),
    ]


def demo_enrichment(company: str, city: str, state: str) -> Enrichment:
    retrieved_at = datetime.now(UTC)
    market = f"{city}, {state}"
    company_units = _company_units(company)
    city_key = city.lower()
    rent_growth = 8.1 if city_key in {"austin", "charlotte"} else 3.4
    renter_share = 0.61 if city_key in {"austin", "arlington"} else 0.48
    household_growth = 4.4
    unemployment_rate = 3.2
    walkability_score = 72 if city_key == "austin" else 58
    if city_key == "boise":
        rent_growth = 1.1
        renter_share = 0.35
        household_growth = 0.8
        unemployment_rate = 6.5
        walkability_score = 42
    trigger = (
        f"{company} announced regional portfolio expansion"
        if company_units >= 50000
        else None
    )
    return Enrichment(
        market=market,
        coordinates=(30.2672, -97.7431) if city_key == "austin" else None,
        geo_confidence="high" if city_key == "austin" else "medium",
        census_geo_id=f"fixture-{city_key}-{state.lower()}",
        renter_share=renter_share,
        median_rent=1840,
        rent_growth_yoy=rent_growth,
        household_growth=household_growth,
        unemployment_rate=unemployment_rate,
        walkability_score=walkability_score,
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
            SourceFact(
                source="Fixture company context",
                label="Asset type fit",
                value="multifamily",
                retrieved_at=retrieved_at,
                confidence="fallback",
            ),
            SourceFact(
                source="Fixture market context",
                label="Household growth",
                value=f"{household_growth:.1f}%",
                retrieved_at=retrieved_at,
                confidence="fallback",
            ),
            SourceFact(
                source="Fixture market context",
                label="Unemployment rate",
                value=f"{unemployment_rate:.1f}% unemployment",
                retrieved_at=retrieved_at,
                confidence="fallback",
            ),
            SourceFact(
                source="Fixture local context",
                label="Walkability score",
                value=str(walkability_score),
                retrieved_at=retrieved_at,
                confidence="fallback",
            ),
        ],
    )


def _company_units(company: str) -> int:
    normalized = company.lower()
    if any(token in normalized for token in ("local", "small")):
        return 8000
    if any(token in normalized for token in ("residential", "living", "property")):
        return 85000
    if any(token in normalized for token in ("homes", "communities")):
        return 42000
    return 12000
