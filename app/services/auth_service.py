"""Authentication service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

    def register(self, request: RegisterRequest) -> TokenResponse:
        if self.repo.get_by_email(request.email):
            raise ValueError("Email đã tồn tại")
        user = User(
            full_name=request.full_name,
            email=request.email,
            password_hash=hash_password(request.password),
            phone=request.phone,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
        )
        self.repo.create(user)
        self.db.commit()
        self.db.refresh(user)
        return TokenResponse(access_token=create_access_token(str(user.id)), refresh_token=create_refresh_token(str(user.id)))

    def login(self, request: LoginRequest) -> TokenResponse:
        user = self.repo.get_by_email(request.email)
        if not user or not verify_password(request.password, user.password_hash):
            raise ValueError("Thông tin đăng nhập không hợp lệ")
        if user.status != UserStatus.ACTIVE:
            raise ValueError("Tài khoản không hoạt động")
        return TokenResponse(access_token=create_access_token(str(user.id)), refresh_token=create_refresh_token(str(user.id)))

    def refresh(self, user_id: int) -> TokenResponse:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("Người dùng không tồn tại")
        return TokenResponse(access_token=create_access_token(str(user.id)), refresh_token=create_refresh_token(str(user.id)))
