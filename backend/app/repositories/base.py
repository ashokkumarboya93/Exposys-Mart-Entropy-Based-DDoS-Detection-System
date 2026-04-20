"""
Base Repository — Generic CRUD Operations
-------------------------------------------
Provides reusable query patterns for all model repositories.
"""

from __future__ import annotations

from typing import Generic, TypeVar, Type, List, Optional, Dict, Any

from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from app.core.database import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """
    Generic repository with common CRUD operations.

    Usage:
        class UserRepo(BaseRepository[User]):
            model = User
    """

    model: Type[T]

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Create ───────────────────────────────────────────────────

    def create(self, **kwargs) -> T:
        """Create and persist a new record."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def create_no_commit(self, **kwargs) -> T:
        """Create a record without committing (for batch operations)."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        return instance

    def bulk_create(self, items: List[Dict[str, Any]]) -> List[T]:
        """Create multiple records in a single transaction."""
        instances = [self.model(**item) for item in items]
        self.db.add_all(instances)
        self.db.commit()
        return instances

    # ── Read ─────────────────────────────────────────────────────

    def get_by_id(self, id: int) -> Optional[T]:
        """Get a single record by primary key."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Get all records with pagination."""
        return (
            self.db.query(self.model)
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_recent(
        self,
        limit: int = 50,
        order_by: str = "timestamp",
        descending: bool = True,
    ) -> List[T]:
        """Get recent records ordered by a timestamp column."""
        col = getattr(self.model, order_by, None)
        if col is None:
            col = getattr(self.model, "id")
        order = desc(col) if descending else asc(col)
        return self.db.query(self.model).order_by(order).limit(limit).all()

    def count(self) -> int:
        """Count all records."""
        return self.db.query(self.model).count()

    def exists(self, **filters) -> bool:
        """Check if a record matching filters exists."""
        q = self.db.query(self.model)
        for key, val in filters.items():
            q = q.filter(getattr(self.model, key) == val)
        return q.first() is not None

    # ── Update ───────────────────────────────────────────────────

    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update a record by primary key."""
        instance = self.get_by_id(id)
        if not instance:
            return None
        for key, val in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, val)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    # ── Delete ───────────────────────────────────────────────────

    def delete(self, id: int) -> bool:
        """Delete a record by primary key."""
        instance = self.get_by_id(id)
        if not instance:
            return False
        self.db.delete(instance)
        self.db.commit()
        return True

    def delete_all(self) -> int:
        """Delete all records. Returns count deleted."""
        count = self.db.query(self.model).delete()
        self.db.commit()
        return count

    # ── Transaction Helpers ──────────────────────────────────────

    def commit(self) -> None:
        """Commit the current transaction."""
        self.db.commit()

    def flush(self) -> None:
        """Flush pending changes without committing."""
        self.db.flush()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.db.rollback()
