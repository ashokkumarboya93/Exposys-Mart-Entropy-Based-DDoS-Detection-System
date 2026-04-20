"""
Entropy Repository
-------------------
Queries for historical entropy data used in trend charts.
"""

from __future__ import annotations

from typing import List, Dict

from app.models.db_models import EntropyHistory
from app.repositories.base import BaseRepository


class EntropyRepository(BaseRepository[EntropyHistory]):
    model = EntropyHistory

    def get_trend_data(self, limit: int = 60) -> List[Dict]:
        """Get formatted entropy history for charts."""
        # Get recent records (descending), but return in chronological order (ascending)
        history = self.get_recent(limit=limit, order_by="timestamp")
        
        return [
            {
                "timestamp": h.timestamp.isoformat() if h.timestamp else "",
                "entropy": h.entropy_value,
                "normalized": h.normalized_entropy,
                "baseline": h.baseline_entropy,
                "threshold": h.threshold,
                "status": h.status,
                "total_requests": h.total_requests,
                "unique_ips": h.unique_ips,
            }
            for h in reversed(history)
        ]
