"""Authorization helpers for user ownership and roles."""

from __future__ import annotations

from app.models.user import User, UserRole


def is_admin(user: User) -> bool:
    return user.role == UserRole.ADMIN


def ensure_owner_or_admin(user: User, owner_id: int) -> None:
    if not (is_admin(user) or user.id == owner_id):
        raise PermissionError("Không có quyền truy cập dữ liệu này")
