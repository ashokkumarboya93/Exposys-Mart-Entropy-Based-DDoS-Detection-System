"""
SQLAlchemy ORM Models
-----------------------
Maps to EXISTING MySQL tables in exposys_mart database
AND defines new tables for the expanded platform.

Existing tables (MySQL Workbench):
  - hacker_attack_sessions
  - hacker_attack_logs
  - store_products
  - analytics_reports

New tables (auto-created on startup):
  - users, admin_users, hacker_users
  - traffic_events, session_logs, attack_sessions
  - suspicious_ips, entropy_history
  - request_logs, downloadable_reports
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    Text, JSON, Index, DECIMAL, TIMESTAMP, ForeignKey,
)

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


# =====================================================================
#  EXISTING MYSQL TABLES (from MySQL Workbench)
#  These models map to tables that already exist in exposys_mart.
#  extend_existing=True prevents conflicts on re-declaration.
# =====================================================================

class HackerAttackSession(Base):
    """Maps to existing hacker_attack_sessions table."""
    __tablename__ = "hacker_attack_sessions"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    attacker_id = Column(Integer, nullable=True)
    attack_type = Column(String(50), nullable=True)
    status = Column(String(50), nullable=True)
    started_at = Column(TIMESTAMP, nullable=True)
    ended_at = Column(TIMESTAMP, nullable=True)


class HackerAttackLog(Base):
    """Maps to existing hacker_attack_logs table."""
    __tablename__ = "hacker_attack_logs"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("hacker_attack_sessions.id"), nullable=True)
    ip_address = Column(String(50), nullable=True)
    requests_sent = Column(Integer, nullable=True)
    timestamp = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")


class StoreProduct(Base):
    """Maps to existing store_products table."""
    __tablename__ = "store_products"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    brand = Column(String(100), nullable=True)
    price = Column(DECIMAL(10, 2), nullable=True)
    original_price = Column(DECIMAL(10, 2), nullable=True)
    image = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    rating = Column(Float, nullable=True)
    reviews = Column(Integer, nullable=True)
    badge = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    specs = Column(JSON, nullable=True)


class ExistingAnalyticsReport(Base):
    """Maps to existing analytics_reports table (Workbench version)."""
    __tablename__ = "analytics_reports"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_type = Column(String(50), nullable=True)
    data = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")


# =====================================================================
#  NEW PLATFORM TABLES (auto-created by SQLAlchemy)
# =====================================================================

# ── User Authentication ─────────────────────────────────────────────

class User(Base):
    """Store customer users."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(128), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(128), default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class StoreOrder(Base):
    """Orders placed by users."""
    __tablename__ = "store_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(50), default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class StoreOrderItem(Base):
    """Items within a store order."""
    __tablename__ = "store_order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("store_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("store_products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    price_at_purchase = Column(DECIMAL(10, 2), nullable=False)


class AdminUser(Base):
    """Admin dashboard users."""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(30), default="admin")
    created_at = Column(DateTime, default=datetime.utcnow)


class HackerUser(Base):
    """Hacker console users."""
    __tablename__ = "hacker_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    alias = Column(String(64), default="phantom")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ── Traffic & Detection ─────────────────────────────────────────────

class TrafficEvent(Base):
    __tablename__ = "traffic_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    endpoint = Column(String(255), default="/")
    method = Column(String(10), default="GET")
    user_agent = Column(String(512), default="")
    traffic_type = Column(String(20), default="normal")
    session_id = Column(String(64), nullable=True, index=True)
    product_id = Column(Integer, nullable=True)
    action = Column(String(50), default="pageview")
    request_count = Column(Integer, default=1)

    __table_args__ = (
        Index("ix_traffic_ip_ts", "ip_address", "timestamp"),
        Index("ix_traffic_type_ts", "traffic_type", "timestamp"),
    )


class SessionLog(Base):
    __tablename__ = "session_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    pages_visited = Column(Integer, default=1)
    total_interactions = Column(Integer, default=1)
    ip_address = Column(String(45), default="")
    is_active = Column(Boolean, default=True)


class AttackEvent(Base):
    """Platform-generated attack events (from attack engine)."""
    __tablename__ = "attack_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    attack_id = Column(String(64), default=_uuid, unique=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    preset_type = Column(String(30), nullable=False)
    num_ips = Column(Integer, default=3)
    requests_per_ip = Column(Integer, default=200)
    total_requests = Column(Integer, default=0)
    status = Column(String(20), default="completed")
    duration_ms = Column(Integer, default=0)
    ips_used = Column(JSON, default=list)


class SuspiciousIP(Base):
    __tablename__ = "suspicious_ips"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(45), unique=True, nullable=False, index=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    total_requests = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
    is_blocked = Column(Boolean, default=False)
    traffic_share = Column(Float, default=0.0)


class EntropyHistory(Base):
    __tablename__ = "entropy_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    entropy_value = Column(Float, default=0.0)
    normalized_entropy = Column(Float, default=0.0)
    max_possible_entropy = Column(Float, default=0.0)
    baseline_entropy = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    status = Column(String(30), default="NORMAL")
    total_requests = Column(Integer, default=0)
    unique_ips = Column(Integer, default=0)


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ip = Column(String(45), nullable=False, index=True)
    endpoint = Column(String(255), default="/")
    method = Column(String(10), default="GET")
    status_code = Column(Integer, default=200)
    response_ms = Column(Integer, default=0)
    traffic_type = Column(String(20), default="normal")

    __table_args__ = (
        Index("ix_reqlog_ip_ts", "ip", "timestamp"),
    )


class DownloadableReport(Base):
    __tablename__ = "downloadable_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(64), unique=True, index=True)
    type = Column(String(20), default="json")
    title = Column(String(255), default="")
    data_json = Column(Text, default="{}")
    file_path = Column(String(512), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
