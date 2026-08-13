"""FastAPI application entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text
import uvicorn

if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.itineraries import router as itineraries_router
from app.api.users import router as users_router
from app.web import router as web_router
from app.core.logging_config import configure_logging
from app.core.responses import error

configure_logging()
project_root = Path(__file__).resolve().parent.parent

app = FastAPI(title="Personalized Travel Planner", debug=True)
app.mount("/static", StaticFiles(directory=project_root / "app" / "static"), name="static")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(itineraries_router)
app.include_router(admin_router)
app.include_router(web_router)


@app.on_event("startup")
def on_startup() -> None:
    from app.database import Base, get_engine
    import app.models

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    ensure_current_schema(engine)


def ensure_current_schema(engine) -> None:
    """Add missing columns for existing SSMS databases without dropping data."""

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names(schema="dbo") or inspector.get_table_names())

    with engine.begin() as connection:
        if "users" in table_names:
            user_columns = {column["name"] for column in inspector.get_columns("users", schema="dbo")}
            if "address" not in user_columns:
                connection.execute(text("ALTER TABLE [dbo].[users] ADD [address] NVARCHAR(500) NULL"))

        if "itineraries" in table_names:
            itinerary_columns = {column["name"] for column in inspector.get_columns("itineraries", schema="dbo")}

            if "spent_amount" not in itinerary_columns:
                connection.execute(text("ALTER TABLE [dbo].[itineraries] ADD [spent_amount] FLOAT NULL"))
                if "total_budget" in itinerary_columns:
                    connection.execute(text("UPDATE [dbo].[itineraries] SET [spent_amount] = [total_budget] WHERE [spent_amount] IS NULL"))
                connection.execute(text("UPDATE [dbo].[itineraries] SET [spent_amount] = 0 WHERE [spent_amount] IS NULL"))
                connection.execute(text("ALTER TABLE [dbo].[itineraries] ALTER COLUMN [spent_amount] FLOAT NOT NULL"))

            if "details" not in itinerary_columns:
                connection.execute(text("ALTER TABLE [dbo].[itineraries] ADD [details] NVARCHAR(MAX) NULL"))



@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return error(str(exc), code=400)


@app.exception_handler(PermissionError)
async def permission_error_handler(_: Request, exc: PermissionError) -> JSONResponse:
    return error(str(exc), code=403)


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return error("Dữ liệu đầu vào không hợp lệ", code=422, details=exc.errors())


@app.get("/api")
def root() -> dict[str, str]:
    return {"message": "Personalized Travel Planner API"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
