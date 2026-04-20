"""
Application Configuration Module
---------------------------------
Centralizes all configuration using Pydantic Settings.
Supports MySQL (production) and SQLite (fallback).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "Exposys Mart Security Analytics Platform"
    APP_VERSION: str = "3.0.0"
    APP_DESCRIPTION: str = (
        "Enterprise-grade entropy-based DDoS detection system "
        "with realistic e-commerce simulation, JWT auth, and MySQL."
    )
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # ── Server ───────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = True

    # ── CORS ─────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["*"]

    # ── Logging ──────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    LOG_FILE: Optional[str] = "logs/app.log"

    # ── Database ─────────────────────────────────────────────────
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/exposys_mart"

    # ── JWT Authentication ───────────────────────────────────────
    JWT_SECRET_KEY: str = "exposysmart-jwt-secret-key-change-in-production-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Detection Thresholds ─────────────────────────────────────
    ENTROPY_THRESHOLD_RATIO: float = 0.7
    BASELINE_SAMPLE_COUNT: int = 5

    # ── Admin Auth (for seeding) ─────────────────────────────────
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # ── Redis (Optional) ─────────────────────────────────────────
    REDIS_URL: Optional[str] = None
    REDIS_TTL: int = 300
    WS_HEARTBEAT_INTERVAL: int = 30

    # ── Rate Limiting ────────────────────────────────────────────
    RATE_LIMIT: str = "100/minute"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.DATABASE_URL


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
