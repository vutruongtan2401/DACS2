"""Generate PDF exports for itineraries."""

from __future__ import annotations

from pathlib import Path

from app.config import get_settings
from app.models.itinerary import Itinerary


class PDFService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_pdf(self, itinerary: Itinerary) -> Path:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except Exception as exc:  # pragma: no cover - optional dependency guard
            raise RuntimeError("ReportLab chưa được cài đặt") from exc

        output_dir = Path(self.settings.pdf_output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = output_dir / f"itinerary-{itinerary.id}.pdf"
        pdf = canvas.Canvas(str(pdf_path), pagesize=A4)
        width, height = A4

        y = height - 40
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(40, y, self.settings.app_name)
        y -= 24
        pdf.setFont("Helvetica", 11)
        lines = [
            f"Tên chuyến đi: {itinerary.trip_title}",
            f"Điểm xuất phát: {itinerary.origin}",
            f"Điểm đến: {itinerary.destination}",
            f"Ngày: {itinerary.start_date} - {itinerary.end_date}",
            f"Số ngày: {itinerary.number_of_days}",
            f"Ngân sách: {itinerary.total_budget} {itinerary.currency}",
            f"Tổng chi phí dự kiến: {itinerary.estimated_total_cost or 0}",
        ]
        for line in lines:
            pdf.drawString(40, y, line)
            y -= 18
        pdf.save()
        return pdf_path
