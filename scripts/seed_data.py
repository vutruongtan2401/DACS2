"""Seed default destinations and demo stats."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

from app.database import get_session
from app.models.destination import Destination
from app.models.system_stat import SystemStat


def main() -> int:
    db = get_session()
    try:
        if not db.query(Destination).count():
            db.add_all(
                [
                    Destination(name="Đà Nẵng", province_or_city="Đà Nẵng", country="Việt Nam", description="Thành phố biển đáng sống"),
                    Destination(name="Đà Lạt", province_or_city="Lâm Đồng", country="Việt Nam", description="Thành phố ngàn hoa"),
                    Destination(name="Phú Quốc", province_or_city="Kiên Giang", country="Việt Nam", description="Đảo nghỉ dưỡng nổi tiếng"),
                ]
            )
        if not db.query(SystemStat).filter(SystemStat.stat_date == date.today()).first():
            db.add(SystemStat(stat_date=date.today()))
        db.commit()
        print("Seed data completed.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
