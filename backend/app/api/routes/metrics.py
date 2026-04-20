"""
Metrics Routes
----------------
Endpoints for retrieving system metrics and analytics.

Endpoints:
    GET /metrics → Full system metrics dashboard data
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_aggregator
from app.models.schemas import MetricsResponse
from app.services.metrics_aggregator import MetricsAggregator
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/metrics", tags=["Metrics & Analytics"])


@router.get(
    "",
    response_model=MetricsResponse,
    summary="Get System Metrics",
    description=(
        "Returns aggregated system metrics including total requests, "
        "unique IPs, entropy value, detection status, and traffic distribution."
    ),
    status_code=status.HTTP_200_OK,
)
async def get_metrics(
    aggregator: MetricsAggregator = Depends(get_aggregator),
) -> MetricsResponse:
    """
    Retrieve current system metrics.

    Returns:
        - total_requests: Total request count across all IPs
        - unique_ips: Number of unique IP addresses
        - entropy: Current Shannon entropy value
        - status: Detection status (NORMAL / DDOS_ATTACK / INSUFFICIENT_DATA)
        - severity: Severity level (safe / warning / critical)
        - traffic_distribution: Top IPs by request count
        - suspicious_ips: IPs flagged by the detection engine
    """
    try:
        metrics = await aggregator.get_metrics()

        logger.debug(
            "API: Metrics served — status=%s, entropy=%.4f, requests=%d",
            metrics.status.value,
            metrics.entropy,
            metrics.total_requests,
        )

        return metrics
    except Exception as exc:
        logger.exception("Failed to aggregate metrics: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metrics aggregation failed: {str(exc)}",
        )
