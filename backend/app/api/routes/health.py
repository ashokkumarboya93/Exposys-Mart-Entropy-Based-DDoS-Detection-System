"""
Health & Diagnostics Routes
-----------------------------
Endpoints for application health monitoring, liveness probes,
and database connection testing.

Endpoints:
    GET /health   -> Basic health check
    GET /test-db  -> MySQL connection test + query hacker_attack_sessions
"""

from __future__ import annotations

import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db, test_connection
from app.models.db_models import HackerAttackSession, HackerAttackLog
from app.models.schemas import HealthResponse

router = APIRouter(tags=["Health"])

# Track application start time for uptime calculation
_start_time = time.monotonic()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns application health status, version, and uptime.",
)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint for load balancers and monitoring.

    Returns:
        Health status with version, environment, and uptime info
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        uptime_seconds=round(time.monotonic() - _start_time, 2),
    )


@router.get(
    "/test-db",
    summary="Test Database Connection",
    description="Verifies MySQL connection and queries hacker_attack_sessions table.",
)
async def test_database(db: Session = Depends(get_db)):
    """
    Test endpoint that:
    1. Verifies the MySQL connection is alive
    2. Queries the existing hacker_attack_sessions table
    3. Queries the existing hacker_attack_logs table
    4. Returns all rows as JSON
    """
    # Step 1: Connection diagnostics
    conn_info = test_connection()

    if not conn_info.get("connected"):
        return {
            "success": False,
            "message": "Database connection FAILED",
            "error": conn_info.get("error", "Unknown error"),
            "connection": conn_info,
        }

    # Step 2: Query hacker_attack_sessions
    sessions = db.query(HackerAttackSession).all()
    sessions_data = [
        {
            "id": s.id,
            "attacker_id": s.attacker_id,
            "attack_type": s.attack_type,
            "status": s.status,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "ended_at": s.ended_at.isoformat() if s.ended_at else None,
        }
        for s in sessions
    ]

    # Step 3: Query hacker_attack_logs
    logs = db.query(HackerAttackLog).all()
    logs_data = [
        {
            "id": l.id,
            "session_id": l.session_id,
            "ip_address": l.ip_address,
            "requests_sent": l.requests_sent,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None,
        }
        for l in logs
    ]

    return {
        "success": True,
        "message": "MySQL connection OK - read/write verified",
        "connection": conn_info,
        "data": {
            "hacker_attack_sessions": {
                "rows": sessions_data,
                "total": len(sessions_data),
            },
            "hacker_attack_logs": {
                "rows": logs_data,
                "total": len(logs_data),
            },
        },
    }
