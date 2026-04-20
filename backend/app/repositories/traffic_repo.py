"""
Traffic Event Repository
--------------------------
Queries for customer and attack traffic events.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import func, desc

from app.models.db_models import TrafficEvent
from app.repositories.base import BaseRepository


class TrafficRepository(BaseRepository[TrafficEvent]):
    model = TrafficEvent

    def get_by_ip(self, ip_address: str, limit: int = 100) -> List[TrafficEvent]:
        """Get traffic events for a specific IP."""
        return (
            self.db.query(TrafficEvent)
            .filter(TrafficEvent.ip_address == ip_address)
            .order_by(desc(TrafficEvent.timestamp))
            .limit(limit)
            .all()
        )

    def get_by_type(self, traffic_type: str, limit: int = 100) -> List[TrafficEvent]:
        """Get traffic events filtered by type (normal/attack)."""
        return (
            self.db.query(TrafficEvent)
            .filter(TrafficEvent.traffic_type == traffic_type)
            .order_by(desc(TrafficEvent.timestamp))
            .limit(limit)
            .all()
        )

    def get_type_counts(self, hours: int = 24) -> Dict[str, int]:
        """Get normal vs attack traffic counts for the last N hours."""
        since = datetime.utcnow() - timedelta(hours=hours)
        rows = (
            self.db.query(
                TrafficEvent.traffic_type,
                func.count(TrafficEvent.id).label("count"),
                func.sum(TrafficEvent.request_count).label("total"),
            )
            .filter(TrafficEvent.timestamp >= since)
            .group_by(TrafficEvent.traffic_type)
            .all()
        )
        result = {"normal": 0, "attack": 0}
        for row in rows:
            if row.traffic_type in result:
                result[row.traffic_type] = row.total or 0
        return result

    def get_top_endpoints(self, traffic_type: str = "attack", limit: int = 10) -> List[Dict]:
        """Get most targeted endpoints by traffic type."""
        rows = (
            self.db.query(
                TrafficEvent.endpoint,
                func.count(TrafficEvent.id).label("hit_count"),
                func.sum(TrafficEvent.request_count).label("total_requests"),
            )
            .filter(TrafficEvent.traffic_type == traffic_type)
            .group_by(TrafficEvent.endpoint)
            .order_by(desc("total_requests"))
            .limit(limit)
            .all()
        )
        return [
            {
                "endpoint": r.endpoint,
                "hit_count": r.hit_count,
                "total_requests": r.total_requests or 0,
            }
            for r in rows
        ]

    def get_hourly_heatmap(self, hours: int = 24) -> List[Dict]:
        """Get request counts grouped by hour for heatmap visualization."""
        since = datetime.utcnow() - timedelta(hours=hours)
        rows = (
            self.db.query(
                func.strftime("%Y-%m-%d %H:00", TrafficEvent.timestamp).label("hour"),
                TrafficEvent.traffic_type,
                func.sum(TrafficEvent.request_count).label("total"),
            )
            .filter(TrafficEvent.timestamp >= since)
            .group_by("hour", TrafficEvent.traffic_type)
            .order_by("hour")
            .all()
        )
        return [
            {
                "hour": r.hour,
                "traffic_type": r.traffic_type,
                "total": r.total or 0,
            }
            for r in rows
        ]

    def get_recent_logs(
        self,
        limit: int = 100,
        traffic_type: Optional[str] = None,
    ) -> List[Dict]:
        """Get formatted recent traffic logs for the admin panel."""
        query = self.db.query(TrafficEvent).order_by(desc(TrafficEvent.timestamp))
        if traffic_type:
            query = query.filter(TrafficEvent.traffic_type == traffic_type)
        events = query.limit(limit).all()

        return [
            {
                "id": e.id,
                "timestamp": e.timestamp.isoformat() if e.timestamp else "",
                "ip": e.ip_address,
                "endpoint": e.endpoint,
                "method": e.method,
                "traffic_type": e.traffic_type,
                "action": e.action,
                "request_count": e.request_count,
                "session_id": (e.session_id or "")[:12],
            }
            for e in events
        ]
