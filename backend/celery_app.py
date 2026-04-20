"""
Celery Application Factory
---------------------------
Async task queue for background metrics and heavy processing.
Falls back to synchronous execution if Redis is not configured.
"""

from __future__ import annotations

import os
from celery import Celery

from app.core.config import settings

# Determine broker URL logic
broker_url = settings.REDIS_URL if settings.REDIS_URL else "memory://"

celery_app = Celery(
    "exposysmart",
    broker=broker_url,
    backend=broker_url,
    include=["tasks.attack_tasks", "tasks.report_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_always_eager=True if broker_url == "memory://" else False,
    task_eager_propagates=True if broker_url == "memory://" else False,
)

if __name__ == "__main__":
    celery_app.start()
