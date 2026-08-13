"""User profile service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import PasswordUpdateRequest, UserUpdateRequest


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

    def update_profile(self, user: User, request: UserUpdateRequest) -> User:
        user.full_name = request.full_name
        user.phone = request.phone
        user.address = request.address
        user.avatar_url = request.avatar_url
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, request: PasswordUpdateRequest) -> None:
        if not verify_password(request.current_password, user.password_hash):
            raise ValueError("Mật khẩu hiện tại không đúng")
        user.password_hash = hash_password(request.new_password)
        self.db.commit()

    def delete_account(self, user: User) -> None:
        self.repo.delete(user)
        self.db.commit()
