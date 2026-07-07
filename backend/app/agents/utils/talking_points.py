"""Talking-point formatting helpers for Signal lead intelligence."""

from app.schemas.lead import Enrichment


def talking_points_for_enrichment(enrichment: Enrichment) -> list[str]:
    """Return rep-facing talking points from normalized enrichment."""
    points: list[str] = []
    if enrichment.renter_share is not None:
        points.append(
            f"{enrichment.market} renter share is {enrichment.renter_share:.0%}."
        )
    if enrichment.rent_growth_yoy is not None:
        points.append(
            f"Local rent growth is {enrichment.rent_growth_yoy:.1f}% year over year."
        )
    if enrichment.company_units:
        points.append(
            f"Portfolio scale signal: about {enrichment.company_units:,} units."
        )
    return points
