"""Create an initial admin account."""

from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

from app.core.security import hash_password
from app.database import get_session
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository


def main() -> int:
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    full_name = os.getenv("ADMIN_FULL_NAME", "Administrator")
    if not email or not password:
        print("Set ADMIN_EMAIL and ADMIN_PASSWORD before running this script.")
        return 1

    db = get_session()
    try:
        repo = UserRepository(db)
        if repo.get_by_email(email):
            print("Admin already exists.")
            return 0
        admin = User(full_name=full_name, email=email, password_hash=hash_password(password), role=UserRole.ADMIN, status=UserStatus.ACTIVE)
        repo.create(admin)
        db.commit()
        print("Admin account created.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
