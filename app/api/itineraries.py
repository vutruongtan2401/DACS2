"""Itinerary routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.responses import success
from app.dependencies import get_current_user, get_db
from app.schemas.itinerary import (
    ItineraryDetailResponse,
    ItineraryListItemResponse,
    ItineraryUpdateRequest,
    TimelineResponse,
    TravelPlanRequest,
)
from app.services.itinerary_service import ItineraryService

router = APIRouter(prefix="/api/itineraries", tags=["itineraries"])


@router.post("")
def create_itinerary(request: TravelPlanRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    itinerary = ItineraryService(db).create(current_user, request)
    return success(ItineraryDetailResponse.model_validate(itinerary).model_dump(), message="Da tao chuyen di")


@router.get("")
def list_itineraries(
    search: str | None = Query(default=None),
    status_value: str | None = Query(default=None, alias="status"),
    offset: int = 0,
    limit: int = 20,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = ItineraryService(db).list(current_user, search=search, status=status_value, offset=offset, limit=limit)
    return success([ItineraryListItemResponse.model_validate(item).model_dump() for item in items])


@router.get("/{itinerary_id}", response_model=ItineraryDetailResponse)
def get_itinerary(itinerary_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return ItineraryService(db).get(current_user, itinerary_id)


@router.put("/{itinerary_id}", response_model=ItineraryDetailResponse)
def update_itinerary(
    itinerary_id: int,
    request: ItineraryUpdateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ItineraryService(db).update(current_user, itinerary_id, request)


@router.delete("/{itinerary_id}")
def delete_itinerary(itinerary_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    ItineraryService(db).delete(current_user, itinerary_id)
    return success(message="Da xoa chuyen di thanh cong")


@router.get("/{itinerary_id}/timeline", response_model=TimelineResponse)
def timeline(itinerary_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return ItineraryService(db).get_timeline(current_user, itinerary_id)


@router.get("/{itinerary_id}/pdf")
def pdf(itinerary_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    pdf_path = ItineraryService(db).export_pdf(current_user, itinerary_id)
    return FileResponse(path=str(pdf_path), filename=pdf_path.name, media_type="application/pdf")
