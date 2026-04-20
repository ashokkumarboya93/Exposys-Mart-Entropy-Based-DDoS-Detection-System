"""
Report Repository
-------------------
Repository for storing and retrieving generated Analytics Reports and Downloadable files.
"""

from __future__ import annotations

import json
from typing import Optional, Dict, Any, List

from app.models.db_models import ExistingAnalyticsReport, DownloadableReport
from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository[ExistingAnalyticsReport]):
    """Repository for ExistingAnalyticsReport."""
    model = ExistingAnalyticsReport
    
    def get_latest(self) -> Optional[ExistingAnalyticsReport]:
        """Get the most recently generated report."""
        recent = self.get_recent(limit=1)
        return recent[0] if recent else None


class DownloadableReportRepository(BaseRepository[DownloadableReport]):
    """Repository for DownloadableReport."""
    model = DownloadableReport
    
    def store_report(self, report_id: str, report_type: str, title: str, 
                     data_dict: Dict[str, Any], file_path: str = "") -> DownloadableReport:
        """Create a new downloadable report record from JSON data."""
        return self.create(
            report_id=report_id,
            type=report_type,
            title=title,
            data_json=json.dumps(data_dict),
            file_path=file_path
        )
        
    def get_by_report_id(self, report_id: str) -> Optional[DownloadableReport]:
        """Find a report by its unique ID string."""
        return self.db.query(DownloadableReport).filter(
            DownloadableReport.report_id == report_id
        ).first()
