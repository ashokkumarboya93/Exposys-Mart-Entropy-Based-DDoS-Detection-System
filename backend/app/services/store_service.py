"""
Store Service
---------------
Product catalog, session tracking, and traffic generation
for the e-commerce store.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.constants import PRODUCT_CATALOG, CATEGORIES, TrafficConstants
from app.models.db_models import TrafficEvent, SessionLog
from app.utils.logger import get_logger

logger = get_logger(__name__)


class StoreService:
    """Manages the e-commerce store logic and traffic generation."""

    @staticmethod
    def get_products(db: Session, category: Optional[str] = None) -> List[Dict]:
        from app.models.db_models import StoreProduct
        query = db.query(StoreProduct)
        if category and category != "all":
            query = query.filter(StoreProduct.category == category)
        products = query.all()
        return [{
            "id": p.id, "name": p.name, "brand": p.brand, "price": float(p.price) if p.price else 0,
            "original_price": float(p.original_price) if p.original_price else 0,
            "category": p.category, "rating": p.rating, "reviews": p.reviews, "badge": p.badge,
            "image": p.image,
            "description": p.description, "specs": p.specs
        } for p in products]

    @staticmethod
    def get_product(db: Session, product_id: int) -> Optional[Dict]:
        from app.models.db_models import StoreProduct
        p = db.query(StoreProduct).filter(StoreProduct.id == product_id).first()
        if p:
            return {
                "id": p.id, "name": p.name, "brand": p.brand, "price": float(p.price) if p.price else 0,
                "original_price": float(p.original_price) if p.original_price else 0,
                "category": p.category, "rating": p.rating, "reviews": p.reviews, "badge": p.badge,
                "image": p.image,
                "description": p.description, "specs": p.specs
            }
        return None

    @staticmethod
    def get_categories() -> List[Dict]:
        return CATEGORIES

    @staticmethod
    def track_interaction(
        db: Session,
        session_id: str,
        page: str,
        action: str,
        product_id: Optional[int] = None,
        search_query: Optional[str] = None,
    ) -> int:
        """
        Log a store interaction and generate normal traffic.
        Returns the number of traffic requests generated.
        """
        # Generate realistic normal traffic
        num_ips = random.randint(3, 8)
        total_generated = 0

        for _ in range(num_ips):
            ip = f"{TrafficConstants.NORMAL_IP_SUBNET}.{random.randint(1, 254)}"
            req_count = random.randint(1, 3)
            total_generated += req_count

            event = TrafficEvent(
                ip_address=ip,
                endpoint=f"/store/{page}",
                method="GET" if action == "pageview" else "POST",
                traffic_type="normal",
                session_id=session_id,
                product_id=product_id,
                action=action,
                request_count=req_count,
            )
            db.add(event)

        # Update or create session log
        session = db.query(SessionLog).filter(
            SessionLog.session_id == session_id
        ).first()

        if session:
            session.last_active = datetime.utcnow()
            session.pages_visited += 1
            session.total_interactions += 1
        else:
            ip = f"{TrafficConstants.NORMAL_IP_SUBNET}.{random.randint(1, 254)}"
            session = SessionLog(
                session_id=session_id,
                ip_address=ip,
                pages_visited=1,
                total_interactions=1,
            )
            db.add(session)

        db.commit()

        logger.info(
            "Store interaction tracked: page=%s action=%s session=%s traffic=%d",
            page, action, session_id[:8], total_generated,
        )

        return total_generated

    @staticmethod
    def get_active_sessions(db: Session, minutes: int = 30) -> int:
        """
        Count active shopper sessions in the last N minutes.

        Reliability note:
        Uses a union of SessionLog and recent normal TrafficEvent session_ids
        so active shoppers remain accurate even when one source lags.
        """
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        session_log_ids = {
            sid
            for (sid,) in db.query(SessionLog.session_id).filter(
                SessionLog.last_active >= cutoff,
                SessionLog.is_active == True,
                SessionLog.session_id.isnot(None),
                SessionLog.session_id != "",
            ).all()
            if sid
        }

        traffic_session_ids = {
            sid
            for (sid,) in db.query(TrafficEvent.session_id).filter(
                TrafficEvent.timestamp >= cutoff,
                TrafficEvent.traffic_type == "normal",
                TrafficEvent.session_id.isnot(None),
                TrafficEvent.session_id != "",
                ~TrafficEvent.session_id.like("bot-%"),
            ).distinct().all()
            if sid
        }

        return len(session_log_ids | traffic_session_ids)

    @staticmethod
    def get_recent_sessions(
        db: Session,
        limit: int = 20,
        active_minutes: int = 30,
    ) -> List[Dict]:
        """Get recent shopping sessions."""
        active_cutoff = datetime.utcnow() - timedelta(minutes=active_minutes)
        sessions = db.query(SessionLog).order_by(
            SessionLog.last_active.desc()
        ).limit(limit).all()

        return [
            {
                "session_id": s.session_id[:12] + "...",
                "started_at": s.started_at.isoformat() if s.started_at else "",
                "last_active": s.last_active.isoformat() if s.last_active else "",
                "pages_visited": s.pages_visited,
                "total_interactions": s.total_interactions,
                "ip": s.ip_address,
                "is_active": bool(
                    s.is_active and s.last_active and s.last_active >= active_cutoff
                ),
                "duration_min": round(
                    (s.last_active - s.started_at).total_seconds() / 60, 1
                ) if s.last_active and s.started_at else 0,
            }
            for s in sessions
        ]
