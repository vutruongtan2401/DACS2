"""Itinerary orchestration service."""

from __future__ import annotations

from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.permissions import ensure_owner_or_admin
from app.models.itinerary import Itinerary
from app.models.user import User
from app.repositories.itinerary_repository import ItineraryRepository
from app.schemas.itinerary import ItineraryUpdateRequest, TimelineResponse, TravelPlanRequest
from app.services.pdf_service import PDFService


class ItineraryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ItineraryRepository(db)
        self.pdf_service = PDFService()

    def create(self, user: User, request: TravelPlanRequest) -> Itinerary:
        itinerary = Itinerary(
            user_id=user.id,
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.start_date + timedelta(days=request.number_of_days - 1),
            total_budget=request.budget,
            details=request.additional_notes,
        )
        self.repo.create(itinerary)
        self.db.commit()
        self.db.refresh(itinerary)
        return itinerary

    def list(self, user: User, search: str | None = None, status: str | None = None, offset: int = 0, limit: int = 20):
        if user.role.value == "ADMIN":
            return self.repo.list_admin(search=search, offset=offset, limit=limit)
        return self.repo.list_for_user(user.id, search=search, offset=offset, limit=limit)

    def get(self, user: User, itinerary_id: int) -> Itinerary:
        itinerary = self.repo.get_with_details(itinerary_id)
        if not itinerary:
            raise ValueError("Khong tim thay chuyen di")
        ensure_owner_or_admin(user, itinerary.user_id)
        return itinerary

    def update(self, user: User, itinerary_id: int, request: ItineraryUpdateRequest) -> Itinerary:
        itinerary = self.get(user, itinerary_id)
        for key, value in request.model_dump(exclude_unset=True).items():
            if key not in {"destination", "start_date", "end_date", "total_budget", "details"}:
                continue
            setattr(itinerary, key, value)
        self.db.commit()
        self.db.refresh(itinerary)
        return itinerary

    def delete(self, user: User, itinerary_id: int) -> None:
        itinerary = self.get(user, itinerary_id)
        self.repo.delete(itinerary)
        self.db.commit()

    def get_timeline(self, user: User, itinerary_id: int) -> TimelineResponse:
        itinerary = self.get(user, itinerary_id)
        return TimelineResponse(
            itinerary_id=itinerary.id,
            trip_title=itinerary.trip_title,
            destination=itinerary.destination,
            start_date=itinerary.start_date,
            end_date=itinerary.end_date,
            number_of_days=itinerary.number_of_days,
            adults=itinerary.adults,
            children=itinerary.children,
            total_budget=itinerary.total_budget,
            currency=itinerary.currency,
            estimated_total_cost=itinerary.estimated_total_cost,
            days=[],
        )

    def export_pdf(self, user: User, itinerary_id: int):
        itinerary = self.get(user, itinerary_id)
        return self.pdf_service.generate_pdf(itinerary)
