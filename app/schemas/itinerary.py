"""Request schema for generating a personalized travel plan."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _normalize_list(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, list):
        normalized = []
        for value in values:
            item = str(value).strip()
            if item and item not in normalized:
                normalized.append(item)
        return normalized
    if isinstance(values, str):
        normalized = []
        for value in values.split(","):
            item = value.strip()
            if item and item not in normalized:
                normalized.append(item)
        return normalized
    raise TypeError("Danh sách phải là list hoặc chuỗi phân tách bằng dấu phẩy")


class TravelPlanRequest(BaseModel):
    """Input data for creating a travel plan."""

    model_config = ConfigDict(extra="forbid")

    trip_title: str = Field(default="", max_length=255)
    origin: str = Field(default="", max_length=255)
    destination: str = Field(min_length=1, max_length=255)
    start_date: date
    number_of_days: int = Field(ge=1, le=30)
    adults: int = Field(ge=1)
    children: int = Field(ge=0)
    budget: float = Field(gt=0)
    currency: str = Field(default="VND", min_length=1, max_length=12)
    destination_features: list[str] = Field(default_factory=list)
    travel_styles: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    transportation_preference: str = Field(default="", max_length=255)
    accommodation_preference: str = Field(default="", max_length=255)
    dietary_requirements: list[str] = Field(default_factory=list)
    travel_pace: str = Field(default="", max_length=100)
    must_visit_places: list[str] = Field(default_factory=list)
    excluded_activities: list[str] = Field(default_factory=list)
    additional_notes: str = Field(default="", max_length=20_000)
    strict_budget: bool = Field(default=False)
    plan_status: str = Field(default="DRAFT", max_length=50)

    @field_validator("trip_title", "origin", "destination", "currency", "transportation_preference", "accommodation_preference", "travel_pace", "additional_notes", "plan_status", mode="before")
    @classmethod
    def _strip_text(cls, value: Any) -> str:
        return str(value).strip() if value is not None else ""

    @field_validator("plan_status")
    @classmethod
    def _normalize_plan_status(cls, value: str) -> str:
        status_map = {
            "Dự định": "DRAFT",
            "Du dinh": "DRAFT",
            "Đang diễn ra": "GENERATING",
            "Dang dien ra": "GENERATING",
            "Đã hoàn thành": "COMPLETED",
            "Da hoan thanh": "COMPLETED",
        }
        normalized = status_map.get(value, value).upper()
        if normalized not in {"DRAFT", "GENERATING", "COMPLETED", "FAILED", "CANCELLED"}:
            raise ValueError("plan_status không hợp lệ")
        return normalized

    @field_validator("destination_features", "travel_styles", "interests", "dietary_requirements", "must_visit_places", "excluded_activities", mode="before")
    @classmethod
    def _normalize_lists(cls, value: Any) -> list[str]:
        return _normalize_list(value)

    @field_validator("destination")
    @classmethod
    def _validate_destination(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("destination không được để trống")
        return value

    @model_validator(mode="after")
    def _validate_request(self) -> TravelPlanRequest:
        if self.number_of_days > 30:
            raise ValueError("number_of_days phải từ 1 đến 30")
        if self.budget <= 0:
            raise ValueError("budget phải lớn hơn 0")
        return self


class BudgetSuggestionRequest(BaseModel):
    """Trip information used to estimate a minimum viable budget."""

    model_config = ConfigDict(extra="forbid")

    trip_title: str = Field(default="", max_length=255)
    origin: str = Field(default="", max_length=255)
    destination: str = Field(min_length=1, max_length=255)
    start_date: date
    number_of_days: int = Field(ge=1, le=30)
    adults: int = Field(ge=1)
    children: int = Field(ge=0)
    currency: str = Field(default="VND", min_length=1, max_length=12)
    destination_features: list[str] = Field(default_factory=list)
    travel_styles: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    transportation_preference: str = Field(default="", max_length=255)
    accommodation_preference: str = Field(default="", max_length=255)
    dietary_requirements: list[str] = Field(default_factory=list)
    travel_pace: str = Field(default="", max_length=100)
    must_visit_places: list[str] = Field(default_factory=list)
    excluded_activities: list[str] = Field(default_factory=list)
    additional_notes: str = Field(default="", max_length=20_000)

    @field_validator("trip_title", "origin", "destination", "currency", "transportation_preference", "accommodation_preference", "travel_pace", "additional_notes", mode="before")
    @classmethod
    def _strip_text(cls, value: Any) -> str:
        return str(value).strip() if value is not None else ""

    @field_validator("destination_features", "travel_styles", "interests", "dietary_requirements", "must_visit_places", "excluded_activities", mode="before")
    @classmethod
    def _normalize_lists(cls, value: Any) -> list[str]:
        return _normalize_list(value)

    @field_validator("destination")
    @classmethod
    def _validate_destination(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("destination khong duoc de trong")
        return value

    @model_validator(mode="after")
    def _validate_request(self) -> BudgetSuggestionRequest:
        return self


class BudgetSuggestionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    minimum_budget: float = Field(gt=0)
    recommended_budget: float = Field(gt=0)
    currency: str = Field(min_length=1, max_length=12)
    accommodation: float = Field(ge=0)
    transportation: float = Field(ge=0)
    food: float = Field(ge=0)
    tickets: float = Field(ge=0)
    contingency: float = Field(ge=0)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_budget_order(self) -> BudgetSuggestionResponse:
        if self.recommended_budget < self.minimum_budget:
            raise ValueError("recommended_budget phai lon hon hoac bang minimum_budget")
        return self


class PlaceSuggestionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    area: str = Field(default="", max_length=255)
    category: str = Field(default="", max_length=100)
    reason: str = Field(min_length=1, max_length=700)
    estimated_cost: float = Field(default=0, ge=0)
    best_time: str = Field(default="", max_length=100)


class PlaceSuggestionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    destination: str = Field(min_length=1, max_length=255)
    currency: str = Field(default="VND", min_length=1, max_length=12)
    suggestions: list[PlaceSuggestionItem] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ItineraryUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    destination: str | None = Field(default=None, max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    total_budget: float | None = Field(default=None, ge=0)


class ItineraryListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_title: str
    origin: str
    destination: str
    country: str | None = None
    start_date: date
    end_date: date
    number_of_days: int
    adults: int
    children: int
    total_budget: float
    currency: str
    status: str
    created_at: datetime


class ItineraryDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_title: str
    origin: str
    destination: str
    country: str | None = None
    start_date: date
    end_date: date
    number_of_days: int
    adults: int
    children: int
    total_budget: float
    currency: str
    transportation_preference: str | None = None
    accommodation_preference: str | None = None
    travel_pace: str | None = None
    special_requirements: str | None = None
    status: str
    estimated_total_cost: float | None = None
    summary: str | None = None


class TimelineActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    period: str
    start_time: str
    end_time: str
    location_name: str
    address: str
    activity_name: str
    description: str
    estimated_cost: float
    transportation: str | None = None
    travel_time_minutes: int | None = None
    food_suggestion: str | None = None
    sort_order: int
    notes: list[str] = Field(default_factory=list)


class TimelineDayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    day_number: int
    itinerary_date: date
    title: str
    summary: str
    estimated_daily_cost: float
    activities: list[TimelineActivityResponse] = Field(default_factory=list)


class TimelineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    itinerary_id: int
    trip_title: str
    destination: str
    start_date: date
    end_date: date
    number_of_days: int
    adults: int
    children: int
    total_budget: float
    currency: str
    estimated_total_cost: float | None = None
    days: list[TimelineDayResponse] = Field(default_factory=list)




