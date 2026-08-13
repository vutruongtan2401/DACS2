"""Authentication routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.responses import success
from app.core.security import decode_token
from app.dependencies import get_current_user, get_db
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    token = AuthService(db).register(request)
    return success(token.model_dump(), message="Dang ky thanh cong")


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    token = AuthService(db).login(request)
    return success(token.model_dump(), message="Dang nhap thanh cong")


@router.post("/logout")
def logout(current_user=Depends(get_current_user)):
    return success(message="Dang xuat thanh cong")


@router.post("/refresh")
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_token(request.refresh_token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token khong hop le") from exc
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token khong dung loai")
    token = AuthService(db).refresh(int(payload["sub"]))
    return success(token.model_dump(), message="Lam moi token thanh cong")


@router.get("/me", response_model=UserResponse)
def me(current_user=Depends(get_current_user)):
    return current_user
