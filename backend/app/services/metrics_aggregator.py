"""
Metrics Aggregation Service — with DB persistence
"""

from __future__ import annotations

from datetime import datetime

from app.core.database import SessionLocal
from app.models.db_models import EntropyHistory
from app.models.schemas import MetricsResponse
from app.services.detection_engine import DetectionEngine
from app.services.entropy_calculator import EntropyCalculator
from app.services.traffic_simulator import TrafficSimulator
from app.utils.helpers import format_ip_distribution, timestamp_now
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MetricsAggregator:
    def __init__(self) -> None:
        self.traffic_simulator = TrafficSimulator()
        self.entropy_calculator = EntropyCalculator()
        self.detection_engine = DetectionEngine()

    async def get_metrics(self) -> MetricsResponse:
        traffic = self.traffic_simulator.traffic

        # Step 1: Entropy
        entropy_result = await self.entropy_calculator.calculate(traffic)

        # Step 2: Detection
        detection_result = await self.detection_engine.analyze(
            entropy_result=entropy_result,
            traffic=traffic,
        )

        # Step 3: Format
        distribution = format_ip_distribution(traffic, top_n=20)

        # Step 4: Build Response
        metrics = MetricsResponse(
            total_requests=self.traffic_simulator.total_requests,
            unique_ips=self.traffic_simulator.unique_ips,
            entropy=entropy_result.entropy_value,
            normalized_entropy=entropy_result.normalized_entropy,
            status=detection_result.status,
            severity=detection_result.severity,
            baseline_entropy=detection_result.baseline_entropy,
            threshold=detection_result.threshold,
            message=detection_result.message,
            traffic_distribution=distribution,
            suspicious_ips=detection_result.suspicious_ips,
            timestamp=timestamp_now(),
        )

        # Step 5: Persist entropy snapshot to DB
        try:
            db = SessionLocal()
            entry = EntropyHistory(
                entropy_value=entropy_result.entropy_value,
                normalized_entropy=entropy_result.normalized_entropy,
                max_possible_entropy=entropy_result.max_possible_entropy,
                baseline_entropy=detection_result.baseline_entropy,
                threshold=detection_result.threshold,
                status=detection_result.status.value,
                total_requests=self.traffic_simulator.total_requests,
                unique_ips=self.traffic_simulator.unique_ips,
            )
            db.add(entry)
            db.commit()
            db.close()
        except Exception as exc:
            logger.debug("Entropy persist skipped: %s", exc)

        return metrics

    def reset_all(self) -> None:
        self.traffic_simulator.reset()
        self.detection_engine.reset()
        logger.info("🔄 All services reset to initial state")
