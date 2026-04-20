"""
Attack Tasks
-------------
Async celery tasks to execute DDoS workloads.
"""

import asyncio
from typing import Dict, Any

from celery_app import celery_app
from app.core.database import SessionLocal
from app.services.attack_engine import AttackEngine
from app.services.metrics_aggregator import MetricsAggregator

@celery_app.task(bind=True, name="tasks.execute_attack")
def execute_attack_task(self, preset_type: str) -> Dict[str, Any]:
    """Execute the attack flow asynchronously via Celery worker."""
    db = SessionLocal()
    agg = MetricsAggregator()
    
    try:
        # We must use asyncio.run because celery executes sync python
        result = asyncio.run(AttackEngine.launch_preset(preset_type, db, agg))
        return result
    finally:
        db.close()

@celery_app.task(bind=True, name="tasks.execute_custom_attack")
def execute_custom_attack_task(self, config: Dict[str, Any]) -> Dict[str, Any]:
    db = SessionLocal()
    agg = MetricsAggregator()
    
    try:
        result = asyncio.run(AttackEngine.launch_custom(config, db, agg))
        return result
    finally:
        db.close()
