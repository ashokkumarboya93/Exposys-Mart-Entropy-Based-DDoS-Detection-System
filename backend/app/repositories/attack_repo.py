"""
Attack Repository
------------------
Queries for DDoS attack event history.
"""

from __future__ import annotations

from typing import List, Dict

from app.models.db_models import AttackEvent
from app.repositories.base import BaseRepository


class AttackRepository(BaseRepository[AttackEvent]):
    model = AttackEvent

    def get_recent_formatted(self, limit: int = 20) -> List[Dict]:
        """Get formatted attack history for the admin panel and PDF reports."""
        attacks = self.get_recent(limit=limit, order_by="timestamp")
        
        return [
            {
                "attack_id": a.attack_id[:12] if a.attack_id else "",
                "timestamp": a.timestamp.isoformat() if a.timestamp else "",
                "preset_type": a.preset_type,
                "num_ips": a.num_ips,
                "requests_per_ip": a.requests_per_ip,
                "total_requests": a.total_requests,
                "status": a.status,
                "duration_ms": a.duration_ms,
                "ips_used": a.ips_used,
            }
            for a in attacks
        ]
