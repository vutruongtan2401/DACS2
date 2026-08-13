"""Itinerary ORM model."""

from __future__ import annotations

import json
from datetime import date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, Float, ForeignKey, Unicode, UnicodeText, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ItineraryStatus(str, Enum):
    DRAFT = "DRAFT"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Itinerary(Base):
    __tablename__ = "itineraries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    destination: Mapped[str] = mapped_column(Unicode(255), nullable=False, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_budget: Mapped[float] = mapped_column("spent_amount", Float, nullable=False)
    details: Mapped[str | None] = mapped_column(UnicodeText, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="itineraries")

    @property
    def trip_title(self) -> str:
        return self.destination

    @property
    def origin(self) -> str:
        return ""

    @property
    def country(self) -> str:
        return "Viet Nam"

    @property
    def number_of_days(self) -> int:
        return max((self.end_date - self.start_date).days + 1, 1)

    @property
    def adults(self) -> int:
        return len(self._members())

    @property
    def children(self) -> int:
        return 0

    @property
    def currency(self) -> str:
        return "VND"

    @property
    def transportation_preference(self) -> None:
        return None

    @property
    def accommodation_preference(self) -> None:
        return None

    @property
    def travel_pace(self) -> None:
        return None

    @property
    def special_requirements(self) -> str:
        return self.details or ""

    @property
    def status(self) -> str:
        return ItineraryStatus.DRAFT.value

    @property
    def estimated_total_cost(self) -> float:
        return self.total_budget

    @property
    def summary(self) -> str:
        return ""

    def _members(self) -> list[dict]:
        for line in (self.details or "").splitlines():
            label, _, value = line.partition(":")
            normalized_label = label.strip().lower()
            if "vi" in normalized_label and value.strip().startswith("["):
                try:
                    members = json.loads(value.strip() or "[]")
                except json.JSONDecodeError:
                    return []
                return members if isinstance(members, list) else []
        return []
