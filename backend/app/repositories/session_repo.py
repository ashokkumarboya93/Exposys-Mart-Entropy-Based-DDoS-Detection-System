"""
Session Log Repository
-----------------------
Queries for user session tracking.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Dict

from sqlalchemy import desc

from app.models.db_models import SessionLog
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[SessionLog]):
    model = SessionLog

    def get_by_session_id(self, session_id: str) -> SessionLog | None:
        """Get a session log by its UUID string."""
        return self.db.query(SessionLog).filter(SessionLog.session_id == session_id).first()

    def get_active_count(self, minutes: int = 30) -> int:
        """Count active sessions within the last N minutes."""
        since = datetime.utcnow() - timedelta(minutes=minutes)
        return (
            self.db.query(SessionLog)
            .filter(SessionLog.last_active >= since)
            .filter(SessionLog.is_active == True)
            .count()
        )

    def get_recent_formatted(self, limit: int = 20) -> List[Dict]:
        """Get recent sessions formatted for the admin dashboard."""
        sessions = self.get_recent(limit=limit, order_by="last_active")
        
        return [
            {
                "id": s.session_id[:12],
                "ip": s.ip_address,
                "started_at": s.started_at.isoformat() if s.started_at else "",
                "last_active": s.last_active.isoformat() if s.last_active else "",
                "pages": s.pages_visited,
                "interactions": s.total_interactions,
                "is_active": s.is_active,
            }
            for s in sessions
        ]
