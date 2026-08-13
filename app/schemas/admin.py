"""Admin statistics schemas."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class OverviewStatisticsResponse(BaseModel):
    total_users: int
    new_users: int
    total_itineraries: int
    generated_itineraries: int
    average_budget: float | None = None
    most_popular_destination: str | None = None


class SimpleCountResponse(BaseModel):
    label: str
    value: int

