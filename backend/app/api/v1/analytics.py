from fastapi import APIRouter, Depends

from app.schemas.analytics import AnalyticsSummaryResponse
from app.services.lead_service import LeadService, get_lead_service

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def analytics_summary(
    service: LeadService = Depends(get_lead_service),
) -> AnalyticsSummaryResponse:
    return await service.analytics_summary()
