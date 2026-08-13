"""Admin routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.responses import success
from app.dependencies import get_admin_user, get_db
from app.models.user import UserStatus
from app.repositories.itinerary_repository import ItineraryRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin import OverviewStatisticsResponse
from app.schemas.user import UserResponse
from app.services.statistics_service import StatisticsService

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/statistics/overview", response_model=OverviewStatisticsResponse)
def overview(current_admin=Depends(get_admin_user), db: Session = Depends(get_db)):
    return StatisticsService(db).get_overview()


@router.get("/users")
def list_users(offset: int = 0, limit: int = 20, current_admin=Depends(get_admin_user), db: Session = Depends(get_db)):
    items = UserRepository(db).list(offset=offset, limit=limit)
    return success([UserResponse.model_validate(item).model_dump() for item in items])


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_admin=Depends(get_admin_user), db: Session = Depends(get_db)):
    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay nguoi dung")
    return user


@router.put("/users/{user_id}/status")
def update_user_status(user_id: int, status_value: UserStatus, current_admin=Depends(get_admin_user), db: Session = Depends(get_db)):
    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay nguoi dung")
    user.status = status_value
    db.commit()
    return success(message="Da cap nhat trang thai nguoi dung")


@router.get("/itineraries")
def list_admin_itineraries(
    search: str | None = Query(default=None),
    offset: int = 0,
    limit: int = 20,
    current_admin=Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    items = ItineraryRepository(db).list_admin(search=search, offset=offset, limit=limit)
    return success(
        [
            {
                "id": item.id,
                "trip_title": item.trip_title,
                "destination": item.destination,
                "start_date": item.start_date,
                "end_date": item.end_date,
                "spent_amount": item.total_budget,
                "status": item.status,
            }
            for item in items
        ]
    )
