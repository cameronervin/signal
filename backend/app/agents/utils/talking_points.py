"""Talking-point formatting helpers for Signal lead intelligence."""

from app.schemas.lead import Enrichment


def talking_points_for_enrichment(enrichment: Enrichment) -> list[str]:
    """Return rep-facing sales insights from normalized enrichment."""
    points: list[str] = []
    if enrichment.renter_share is not None:
        points.append(
            f"{enrichment.market} has {enrichment.renter_share:.0%} renter "
            "share, a demand signal for leasing volume and prospect follow-up."
        )
    if enrichment.rent_growth_yoy is not None:
        points.append(
            f"Local rent growth is {enrichment.rent_growth_yoy:.1f}% year over "
            "year, which can make response speed and tour conversion more urgent."
        )
    if enrichment.company_units:
        points.append(
            f"Portfolio scale signal: about {enrichment.company_units:,} units, "
            "suggesting follow-up complexity and team-capacity pressure."
        )
    return points
