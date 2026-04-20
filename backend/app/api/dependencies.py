"""
API Dependencies
------------------
Dependency injection for FastAPI routes.
"""

from __future__ import annotations

from functools import lru_cache

from app.core.database import get_db
from app.services.metrics_aggregator import MetricsAggregator


@lru_cache(maxsize=1)
def get_aggregator() -> MetricsAggregator:
    """Singleton factory for the MetricsAggregator."""
    return MetricsAggregator()
