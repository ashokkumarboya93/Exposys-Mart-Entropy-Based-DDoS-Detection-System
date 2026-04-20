"""
Application Lifecycle Events
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.core.security import hash_password
from app.models.db_models import AdminUser, HackerUser

logger = logging.getLogger(__name__)


def _seed_defaults():
    """Ensure default admin and hacker users exist."""
    db = SessionLocal()
    try:
        # Admin
        admin = db.query(AdminUser).filter(AdminUser.username == settings.ADMIN_USERNAME).first()
        if not admin:
            db.add(AdminUser(
                username=settings.ADMIN_USERNAME,
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                role="admin",
            ))
            logger.info("Default admin user created: %s", settings.ADMIN_USERNAME)

        # Hacker
        hacker = db.query(HackerUser).filter(HackerUser.username == "darknet").first()
        if not hacker:
            db.add(HackerUser(
                username="darknet",
                hashed_password=hash_password("ddos@2024"),
                alias="DARKNET",
            ))
            logger.info("Default hacker user created: darknet")

        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning("Default user seeding skipped: %s", exc)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # ── Startup ──────────────────────────────────────────────────
    logger.info(
        "[STARTUP] Starting %s v%s [%s]",
        settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT,
    )

    # Initialize database tables
    init_db()
    logger.info("[DB] Database initialized: %s", settings.DATABASE_URL.split("@")[-1])
    logger.info("[CORS] Allowed origins: %s", settings.ALLOWED_ORIGINS)

    # Seed default users
    _seed_defaults()

    yield

    # ── Shutdown ─────────────────────────────────────────────────
    logger.info("[SHUTDOWN] Stopping %s...", settings.APP_NAME)
    logger.info("[SHUTDOWN] Graceful shutdown complete.")
