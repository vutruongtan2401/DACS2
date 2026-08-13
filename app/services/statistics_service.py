"""Statistics service for admin dashboard."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.statistics_repository import StatisticsRepository


class StatisticsService:
    def __init__(self, db: Session) -> None:
        self.repo = StatisticsRepository(db)

    def get_overview(self) -> dict:
        return self.repo.get_overview()

    def get_itinerary_statistics(self) -> list[dict]:
        return self.repo.list_itinerary_stats()

    def get_destination_statistics(self) -> list[dict]:
        return self.repo.list_destination_stats()
