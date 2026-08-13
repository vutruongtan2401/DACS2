"""Authentication request and response schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)

    @field_validator("password")
    @classmethod
    def password_must_be_72_bytes_or_less(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Mật khẩu không được dài quá 72 byte (khi mã hóa UTF-8)")
        return v

    password: str = Field(min_length=8, max_length=72)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr

    @field_validator("password")
    @classmethod
    def password_must_be_72_bytes_or_less(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Mật khẩu không được dài quá 72 byte (khi mã hóa UTF-8)")
        return v

    password: str = Field(min_length=8, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)
