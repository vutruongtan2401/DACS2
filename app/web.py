"""HTML page routes rendered with Jinja2 templates."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates_dir = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

router = APIRouter(tags=["web"])


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "page_title": "Trang chủ",
        },
    )


@router.get("/auth/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "auth/login.html", {"request": request, "page_title": "Đăng nhập"})


@router.get("/auth/register", response_class=HTMLResponse)
def register_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "auth/register.html", {"request": request, "page_title": "Đăng ký"})


@router.get("/itineraries/create", response_class=HTMLResponse)
def create_itinerary_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "itineraries/create.html", {"request": request, "page_title": "Tạo lịch trình"})


@router.get("/itineraries", response_class=HTMLResponse)
def itineraries_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "itineraries/list.html", {"request": request, "page_title": "Danh sách lịch trình"})


@router.get("/itineraries/{itinerary_id}", response_class=HTMLResponse)
def itinerary_detail_page(request: Request, itinerary_id: int) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "itineraries/detail.html",
        {"request": request, "page_title": "Chi tiết lịch trình", "itinerary_id": itinerary_id},
    )


@router.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "admin/dashboard.html", {"request": request, "page_title": "Dashboard quản trị"})


@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "profile.html", {"request": request, "page_title": "Hồ sơ của tôi"})

