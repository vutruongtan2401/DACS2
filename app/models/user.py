"""User ORM model."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, Unicode, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    INACTIVE = "INACTIVE"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    email: Mapped[str] = mapped_column(Unicode(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(Unicode(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Unicode(500), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Unicode(500), nullable=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, native_enum=False), default=UserRole.USER, nullable=False)
    status: Mapped[UserStatus] = mapped_column(SAEnum(UserStatus, native_enum=False), default=UserStatus.ACTIVE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    itineraries = relationship("Itinerary", back_populates="user", cascade="all, delete-orphan")
