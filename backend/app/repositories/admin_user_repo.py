"""
Admin User Repository
----------------------
Queries for administrator accounts and roles.
"""

from __future__ import annotations

import hashlib
from typing import Optional

from app.models.db_models import AdminUser
from app.repositories.base import BaseRepository


class AdminUserRepository(BaseRepository[AdminUser]):
    model = AdminUser

    def get_by_username(self, username: str) -> Optional[AdminUser]:
        """Find an admin by their unique username."""
        return self.db.query(AdminUser).filter(AdminUser.username == username).first()

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify standard SHA-256 password hash (demo use only)."""
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        return pwd_hash == hashed_password
