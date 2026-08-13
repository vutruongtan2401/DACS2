"""Repository for dashboard statistics."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.itinerary import Itinerary
from app.models.user import User


class StatisticsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_overview(self) -> dict[str, int | float | str | None]:
        total_users = self.db.scalar(select(func.count()).select_from(User)) or 0
        total_itineraries = self.db.scalar(select(func.count()).select_from(Itinerary)) or 0
        average_budget = self.db.scalar(select(func.avg(Itinerary.total_budget)))
        return {
            "total_users": int(total_users),
            "new_users": int(self.db.scalar(select(func.count()).select_from(User).where(func.date(User.created_at) == date.today())) or 0),
            "total_itineraries": int(total_itineraries),
            "generated_itineraries": int(total_itineraries),
            "average_budget": float(average_budget) if average_budget is not None else None,
            "most_popular_destination": None,
        }

    def list_itinerary_stats(self) -> list[dict[str, int | str]]:
        return []

    def list_destination_stats(self) -> list[dict[str, int | str]]:
        return []
