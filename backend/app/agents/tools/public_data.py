"""Public-data tool wrapper for Signal graph nodes."""

from app.infrastructure.public_data import PublicDataClient
from app.schemas.lead import Enrichment, LeadCreate


async def enrich_lead_with_public_data(
    *,
    public_data_client: PublicDataClient,
    lead: LeadCreate,
) -> Enrichment:
    return await public_data_client.enrich(lead)
