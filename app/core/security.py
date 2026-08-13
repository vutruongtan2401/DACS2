"""Password hashing and JWT helpers."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from passlib.context import CryptContext

from app.config import get_settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    header_part = _b64encode_json(header)
    payload_part = _b64encode_json(payload)
    signature = _sign(f"{header_part}.{payload_part}".encode("utf-8"), settings.secret_key.encode("utf-8"))
    return f"{header_part}.{payload_part}.{signature}"


def create_access_token(subject: str) -> str:
    settings = get_settings()
    return create_token(subject, "access", timedelta(minutes=settings.access_token_expire_minutes))


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    return create_token(subject, "refresh", timedelta(days=settings.refresh_token_expire_days))


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        header_part, payload_part, signature_part = token.split(".")
    except ValueError as exc:
        raise ValueError("Token không hợp lệ") from exc

    expected_signature = _sign(f"{header_part}.{payload_part}".encode("utf-8"), settings.secret_key.encode("utf-8"))
    if not hmac.compare_digest(signature_part, expected_signature):
        raise ValueError("Chữ ký token không hợp lệ")

    payload = json.loads(_b64decode(payload_part).decode("utf-8"))
    exp = int(payload.get("exp", 0))
    if exp and datetime.now(timezone.utc).timestamp() > exp:
        raise ValueError("Token đã hết hạn")
    return payload


def _b64encode_json(data: dict[str, Any]) -> str:
    raw = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _sign(message: bytes, secret: bytes) -> str:
    digest = hmac.new(secret, message, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
