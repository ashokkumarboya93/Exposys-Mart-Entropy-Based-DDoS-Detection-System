"""
Database Configuration - SQLAlchemy + MySQL / SQLite
------------------------------------------------------
Connects to the existing MySQL database (exposys_mart)
created via MySQL Workbench.

Connection: mysql+pymysql://root:root@localhost:3306/exposys_mart
"""

from __future__ import annotations

import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

logger = logging.getLogger(__name__)

ACTIVE_DB_URL = settings.DATABASE_URL

if settings.is_sqlite:
    # SQLite fallback for quick prototyping
    engine = create_engine(
        ACTIVE_DB_URL,
        connect_args={"check_same_thread": False, "timeout": 15},
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
else:
    # MySQL production configuration
    # Append charset if not already in URL
    db_url = ACTIVE_DB_URL
    if "charset" not in db_url:
        separator = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{separator}charset=utf8mb4"

    engine = create_engine(
        db_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,       # Reconnect on stale connections
        pool_size=10,             # Maintain 10 persistent connections
        max_overflow=20,          # Allow 20 extra during bursts
        pool_recycle=300,         # Recycle connections every 5 minutes
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency - yields a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Create all tables defined in db_models.py.
    For existing MySQL tables, this is a no-op (CREATE IF NOT EXISTS).
    New tables from our models will be created alongside existing ones.
    """
    from app.models import db_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables synced: %s", ACTIVE_DB_URL.split("@")[-1])


def test_connection() -> dict:
    """
    Test the database connection and return diagnostic info.
    Used by the /test-db endpoint.
    """
    try:
        with engine.connect() as conn:
            # Basic connectivity
            result = conn.execute(text("SELECT 1"))
            result.fetchone()

            # Get database name
            db_result = conn.execute(text("SELECT DATABASE()"))
            db_name = db_result.fetchone()[0]

            # Get table list
            tables_result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in tables_result.fetchall()]

            # Get MySQL version
            ver_result = conn.execute(text("SELECT VERSION()"))
            version = ver_result.fetchone()[0]

        return {
            "connected": True,
            "database": db_name,
            "mysql_version": version,
            "tables": tables,
            "table_count": len(tables),
            "driver": "pymysql",
            "pool_size": engine.pool.size(),
            "url": ACTIVE_DB_URL.split("@")[-1],  # Hide credentials
        }
    except Exception as exc:
        logger.error("Database connection test failed: %s", exc)
        return {
            "connected": False,
            "error": str(exc),
            "url": ACTIVE_DB_URL.split("@")[-1],
        }
