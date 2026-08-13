"""Itinerary repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.itinerary import Itinerary


class ItineraryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, itinerary: Itinerary) -> Itinerary:
        self.db.add(itinerary)
        self.db.flush()
        return itinerary

    def get_by_id(self, itinerary_id: int) -> Itinerary | None:
        return self.db.get(Itinerary, itinerary_id)

    def get_with_details(self, itinerary_id: int) -> Itinerary | None:
        return self.get_by_id(itinerary_id)

    def list_for_user(self, user_id: int, search: str | None = None, status: str | None = None, offset: int = 0, limit: int = 20) -> list[Itinerary]:
        stmt = select(Itinerary).where(Itinerary.user_id == user_id)
        if search:
            stmt = stmt.where(Itinerary.destination.contains(search))
        stmt = stmt.order_by(Itinerary.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())

    def list_admin(self, search: str | None = None, status: str | None = None, offset: int = 0, limit: int = 20) -> list[Itinerary]:
        stmt = select(Itinerary)
        if search:
            stmt = stmt.where(Itinerary.destination.contains(search))
        stmt = stmt.order_by(Itinerary.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())

    def delete(self, itinerary: Itinerary) -> None:
        self.db.delete(itinerary)
