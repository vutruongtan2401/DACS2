"""User schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class UserBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = Field(default=None, max_length=500)


class UserUpdateRequest(UserBase):
    pass


class PasswordUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    current_password: str | None = Field(default=None, min_length=1, max_length=72)
    old_password: str | None = Field(default=None, min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)

    @field_validator("current_password", "new_password")
    @classmethod
    def password_must_be_72_bytes_or_less(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Mat khau khong duoc dai qua 72 byte")
        return value

    @model_validator(mode="after")
    def normalize_current_password(self) -> PasswordUpdateRequest:
        if not self.current_password:
            self.current_password = self.old_password
        if not self.current_password:
            raise ValueError("Vui long nhap mat khau hien tai")
        return self


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: str
    status: str
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None
