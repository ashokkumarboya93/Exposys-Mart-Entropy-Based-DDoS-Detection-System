"""
Repository Layer
------------------
Abstracted data access layer using the repository pattern.
All database operations go through repositories for clean separation.
"""

from app.repositories.base import BaseRepository
from app.repositories.traffic_repo import TrafficRepository
from app.repositories.session_repo import SessionRepository
from app.repositories.attack_repo import AttackRepository
from app.repositories.suspicious_ip_repo import SuspiciousIPRepository
from app.repositories.entropy_repo import EntropyRepository
from app.repositories.report_repo import ReportRepository

__all__ = [
    "BaseRepository",
    "TrafficRepository",
    "SessionRepository",
    "AttackRepository",
    "SuspiciousIPRepository",
    "EntropyRepository",
    "ReportRepository",
]
