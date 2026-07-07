from app.repositories.signal_snapshot import SignalRepository
from app.schemas.analytics import AnalyticsSummaryResponse


class AnalyticsService:
    """Use cases for dashboard and operational analytics."""

    def __init__(self, repository: SignalRepository) -> None:
        self.repository = repository

    async def analytics_summary(self) -> AnalyticsSummaryResponse:
        return await self.repository.analytics_summary()
