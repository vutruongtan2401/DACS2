"""User profile routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.responses import success
from app.dependencies import get_current_user, get_db
from app.schemas.user import PasswordUpdateRequest, UserResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(request: UserUpdateRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return UserService(db).update_profile(current_user, request)


@router.put("/me/password")
def update_password(request: PasswordUpdateRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    UserService(db).update_password(current_user, request)
    return success(message="Đổi mật khẩu thành công")


@router.delete("/me")
def delete_me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    UserService(db).delete_account(current_user)
    return success(message="Xóa tài khoản thành công")
