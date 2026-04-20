"""
Suspicious IP Repository
-------------------------
Tracking and querying potentially malicious IP addresses.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Dict

from sqlalchemy import desc

from app.models.db_models import SuspiciousIP
from app.repositories.base import BaseRepository


class SuspiciousIPRepository(BaseRepository[SuspiciousIP]):
    model = SuspiciousIP

    def get_by_ip(self, ip_address: str) -> SuspiciousIP | None:
        """Get suspicious record for a specific IP."""
        return (
            self.db.query(SuspiciousIP)
            .filter(SuspiciousIP.ip_address == ip_address)
            .first()
        )

    def upsert_ip(
        self,
        ip_address: str,
        request_count: int,
        risk_score: float,
        traffic_share: float = 0.0,
    ) -> SuspiciousIP:
        """Update existing or create new suspicious IP record."""
        record = self.get_by_ip(ip_address)
        if record:
            record.total_requests += request_count
            record.risk_score = max(record.risk_score, risk_score)
            record.last_seen = datetime.utcnow()
            record.traffic_share = max(record.traffic_share, traffic_share)
            
            if record.risk_score >= 90.0:
                record.is_blocked = True
                
            self.db.commit()
            return record
        else:
            return self.create(
                ip_address=ip_address,
                total_requests=request_count,
                risk_score=risk_score,
                traffic_share=traffic_share,
                is_blocked=(risk_score >= 90.0),
            )

    def get_top_offenders(self, limit: int = 20) -> List[Dict]:
        """Get the worst offenders formatted for the admin dashboard."""
        sus_ips = (
            self.db.query(SuspiciousIP)
            .order_by(desc(SuspiciousIP.total_requests))
            .limit(limit)
            .all()
        )
        
        return [
            {
                "ip": s.ip_address,
                "requests": s.total_requests,
                "risk_score": s.risk_score,
                "first_seen": s.first_seen.isoformat() if s.first_seen else "",
                "last_seen": s.last_seen.isoformat() if s.last_seen else "",
                "is_blocked": s.is_blocked,
                "traffic_share": s.traffic_share,
            }
            for s in sus_ips
        ]
