from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_analytics_service
from app.schemas.analytics import AnalyticsSummaryResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def analytics_summary(
    service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsSummaryResponse:
    return await service.analytics_summary()
