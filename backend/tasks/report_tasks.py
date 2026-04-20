"""
Report Tasks
-------------
Async celery tasks to generate downloadable PDF/CSV reports.
"""

import csv
import json
import io
from typing import Dict, Any

from celery_app import celery_app
from app.core.database import SessionLocal
from app.repositories.traffic_repo import TrafficRepository

@celery_app.task(bind=True, name="tasks.generate_csv_report")
def generate_csv_report_task(self, report_id: str) -> str:
    """Generate enormous CSV traffic report in background."""
    db = SessionLocal()
    try:
        repo = TrafficRepository(db)
        logs = repo.get_recent(limit=5000)
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Timestamp", "IP", "Endpoint", "Method", "Type"])
        
        for log in logs:
            writer.writerow([
                log.id, 
                log.timestamp.isoformat() if log.timestamp else "",
                log.ip_address,
                log.endpoint,
                log.method,
                log.traffic_type
            ])
            
        # In a real system, upload output.getvalue() to S3 and return URL
        # For our simulation, we return the string content directly.
        return output.getvalue()
    finally:
        db.close()
