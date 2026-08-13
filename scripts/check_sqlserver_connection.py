"""Check the SQL Server connection configured for the app."""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import text

if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

from app.database import Base, get_engine
import app.models  # noqa: F401 - register metadata


def main() -> int:
    engine = get_engine()
    with engine.begin() as conn:
        database_name = conn.execute(text("SELECT DB_NAME()")).scalar_one()
        if database_name != "TravelPlanner":
            raise RuntimeError(f"Expected TravelPlanner, connected to {database_name!r}")

        Base.metadata.create_all(bind=conn)
        table_count = conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                """
            )
        ).scalar_one()

    print(f"Connected to SQL Server database {database_name}. Tables available: {table_count}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
