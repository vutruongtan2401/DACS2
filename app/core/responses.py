"""Common API response helpers."""

from __future__ import annotations

from typing import Any

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success(data: Any = None, message: str = "Success", code: int = status.HTTP_200_OK) -> JSONResponse:
    return JSONResponse(status_code=code, content=jsonable_encoder({"success": True, "message": message, "data": data}))


def error(message: str, code: int = status.HTTP_400_BAD_REQUEST, details: Any = None) -> JSONResponse:
    payload = {"success": False, "message": message}
    if details is not None:
        payload["details"] = details
    return JSONResponse(status_code=code, content=jsonable_encoder(payload))
