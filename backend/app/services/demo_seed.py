from dataclasses import dataclass

from app.schemas.lead import Enrichment, LeadCreate, SourceFact


@dataclass(frozen=True)
class DemoSeedRecord:
    lead_id: str
    run_id: str
    lead: LeadCreate
    enrichment: Enrichment


class DemoSeedPublicDataClient:
    def __init__(self, records: list[DemoSeedRecord] | None = None) -> None:
        self._enrichment_by_email = {
            str(record.lead.email): record.enrichment
            for record in (records or demo_seed_records())
        }

    async def enrich(self, lead: LeadCreate) -> Enrichment:
        return self._enrichment_by_email[str(lead.email)]


def demo_seed_records() -> list[DemoSeedRecord]:
    return [
        DemoSeedRecord(
            lead_id="lead_demo_a",
            run_id="run_demo_a",
            lead=LeadCreate(
                contact_name="Taylor Reed",
                email="taylor@regionalresidential.example",
                company="Regional Residential Group",
                role="VP Leasing",
                property_address="100 Demo Ave",
                city="Austin",
                state="TX",
                country="US",
            ),
            enrichment=_enrichment(
                market="Austin, TX",
                coordinates=(30.2672, -97.7431),
                renter_share=0.64,
                median_rent=1840,
                rent_growth_yoy=8.1,
                household_growth=4.4,
                unemployment_rate=3.2,
                company_units=85000,
                recent_trigger="Regional Residential Group announced portfolio growth",
            ),
        ),
        DemoSeedRecord(
            lead_id="lead_demo_b",
            run_id="run_demo_b",
            lead=LeadCreate(
                contact_name="Jordan Lee",
                email="jordan@metrocommunities.example",
                company="Metro Communities Group",
                role="Leasing Manager",
                property_address="200 Demo Blvd",
                city="Denver",
                state="CO",
                country="US",
            ),
            enrichment=_enrichment(
                market="Denver, CO",
                coordinates=(39.7392, -104.9903),
                renter_share=0.48,
                median_rent=1725,
                rent_growth_yoy=3.4,
                household_growth=4.4,
                unemployment_rate=3.2,
                company_units=42000,
                recent_trigger=None,
            ),
        ),
        DemoSeedRecord(
            lead_id="lead_demo_c",
            run_id="run_demo_c",
            lead=LeadCreate(
                contact_name="Morgan Ellis",
                email="morgan@localhousing.example",
                company="Local Housing Operator",
                role="Leasing Coordinator",
                property_address="300 Demo Rd",
                city="Toledo",
                state="OH",
                country="US",
            ),
            enrichment=_enrichment(
                market="Toledo, OH",
                coordinates=(41.6528, -83.5379),
                renter_share=0.42,
                median_rent=980,
                rent_growth_yoy=1.0,
                household_growth=0.5,
                unemployment_rate=6.5,
                company_units=8000,
                recent_trigger=None,
            ),
        ),
        DemoSeedRecord(
            lead_id="lead_demo_gate_failed",
            run_id="run_demo_gate_failed",
            lead=LeadCreate(
                contact_name="Casey Novak",
                email="casey@personal.example",
                company="Small Portfolio Operator",
                role="Property Manager",
                property_address="400 Demo St",
                city="Miami",
                state="FL",
                country="US",
            ),
            enrichment=_enrichment(
                market="Miami, FL",
                coordinates=(25.7617, -80.1918),
                renter_share=0.52,
                median_rent=2050,
                rent_growth_yoy=3.4,
                household_growth=2.0,
                unemployment_rate=3.7,
                company_units=12000,
                recent_trigger=None,
            ),
        ),
        DemoSeedRecord(
            lead_id="lead_demo_missing_trigger",
            run_id="run_demo_missing_trigger",
            lead=LeadCreate(
                contact_name="Riley Park",
                email="riley@portfoliohousing.example",
                company="Portfolio Housing Group",
                role="Director of Leasing",
                property_address="500 Demo Way",
                city="Charlotte",
                state="NC",
                country="US",
            ),
            enrichment=_enrichment(
                market="Charlotte, NC",
                coordinates=(35.2271, -80.8431),
                renter_share=0.61,
                median_rent=1620,
                rent_growth_yoy=8.1,
                household_growth=4.4,
                unemployment_rate=3.2,
                company_units=85000,
                recent_trigger=None,
            ),
        ),
        DemoSeedRecord(
            lead_id="lead_demo_warning_only",
            run_id="run_demo_warning_only",
            lead=LeadCreate(
                contact_name="Jamie Ortiz",
                email="jamie@smalloperator.example",
                company="Small Operator Collective",
                role="VP Leasing",
                property_address="600 Demo Ct",
                city="Austin",
                state="TX",
                country="US",
            ),
            enrichment=_enrichment(
                market="Austin, TX",
                coordinates=(30.2672, -97.7431),
                renter_share=0.61,
                median_rent=1840,
                rent_growth_yoy=8.1,
                household_growth=4.4,
                unemployment_rate=3.2,
                company_units=8000,
                recent_trigger=None,
            ),
        ),
    ]


def _enrichment(
    *,
    market: str,
    coordinates: tuple[float, float],
    renter_share: float,
    median_rent: int,
    rent_growth_yoy: float,
    household_growth: float,
    unemployment_rate: float,
    company_units: int,
    recent_trigger: str | None,
) -> Enrichment:
    sources = [
        SourceFact(
            source="Census ACS",
            label="Renter share",
            value=f"{renter_share:.0%}",
        ),
        SourceFact(
            source="Census ACS",
            label="Median rent",
            value=f"${median_rent:,}",
        ),
        SourceFact(
            source="FRED",
            label="Rent growth",
            value=f"{rent_growth_yoy:.1f}% YoY",
        ),
        SourceFact(
            source="DataUSA",
            label="Household growth",
            value=f"{household_growth:.1f}% YoY",
        ),
        SourceFact(
            source="FRED",
            label="Unemployment rate",
            value=f"{unemployment_rate:.1f}%",
        ),
        SourceFact(
            source="Company registry",
            label="Company resolution",
            value="Plausible operating entity",
        ),
        SourceFact(
            source="DNS MX",
            label="Corporate domain MX",
            value="MX records found",
        ),
    ]
    if recent_trigger:
        sources.append(
            SourceFact(
                source="News",
                label="Trigger event",
                value=recent_trigger,
            )
        )
    return Enrichment(
        market=market,
        coordinates=coordinates,
        renter_share=renter_share,
        median_rent=median_rent,
        rent_growth_yoy=rent_growth_yoy,
        household_growth=household_growth,
        unemployment_rate=unemployment_rate,
        company_units=company_units,
        recent_trigger=recent_trigger,
        sources=sources,
    )
