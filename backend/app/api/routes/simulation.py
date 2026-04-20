"""
Simulation Routes
-------------------
Endpoints for generating simulated traffic.

Endpoints:
    POST /simulate/normal  → Generate normal traffic
    POST /simulate/attack  → Generate DDoS attack traffic
    POST /simulate/reset   → Reset all traffic data
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_aggregator
from app.models.enums import TrafficType
from app.models.schemas import AttackSimulationRequest, SimulationResponse
from app.services.metrics_aggregator import MetricsAggregator
from app.utils.helpers import timestamp_now
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/simulate", tags=["Traffic Simulation"])


@router.post(
    "/normal",
    response_model=SimulationResponse,
    summary="Generate Normal Traffic",
    description="Simulates legitimate user traffic with diverse IP distribution.",
    status_code=status.HTTP_200_OK,
)
async def simulate_normal_traffic(
    aggregator: MetricsAggregator = Depends(get_aggregator),
) -> SimulationResponse:
    """
    Generate normal traffic simulating legitimate users.

    - Uses 20-50 random IPs from the 192.168.1.x subnet
    - Each IP sends 1-5 requests
    - Traffic is merged into the existing distribution
    """
    try:
        generated, total = await aggregator.traffic_simulator.generate_normal_traffic()

        logger.info(
            "API: Normal traffic generated — %d IPs, %d requests",
            len(generated),
            total,
        )

        return SimulationResponse(
            success=True,
            message=f"Normal traffic generated: {len(generated)} IPs, {total} requests",
            traffic_type=TrafficType.NORMAL,
            ips_generated=len(generated),
            total_requests_generated=total,
            timestamp=timestamp_now(),
        )
    except Exception as exc:
        logger.exception("Failed to generate normal traffic: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Traffic simulation failed: {str(exc)}",
        )


@router.post(
    "/attack",
    response_model=SimulationResponse,
    summary="Simulate DDoS Attack",
    description="Simulates a DDoS attack with concentrated traffic from few IPs.",
    status_code=status.HTTP_200_OK,
)
async def simulate_attack_traffic(
    request: AttackSimulationRequest,
    aggregator: MetricsAggregator = Depends(get_aggregator),
) -> SimulationResponse:
    """
    Generate DDoS attack traffic.

    - Uses a small number of IPs (configurable, 1-50)
    - Each IP sends high volume requests (configurable, 10-10000)
    - Traffic uses the 10.0.0.x subnet
    """
    try:
        generated, total = await aggregator.traffic_simulator.generate_attack_traffic(
            num_ips=request.num_ips,
            requests_per_ip=request.requests_per_ip,
        )

        logger.warning(
            "API: Attack traffic generated — %d IPs, %d requests (params: ips=%d, rpi=%d)",
            len(generated),
            total,
            request.num_ips,
            request.requests_per_ip,
        )

        return SimulationResponse(
            success=True,
            message=f"Attack traffic generated: {len(generated)} IPs, {total} requests",
            traffic_type=TrafficType.ATTACK,
            ips_generated=len(generated),
            total_requests_generated=total,
            timestamp=timestamp_now(),
        )
    except ValueError as exc:
        logger.error("Invalid attack parameters: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid attack parameters: {str(exc)}",
        )
    except Exception as exc:
        logger.exception("Failed to generate attack traffic: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Attack simulation failed: {str(exc)}",
        )


@router.post(
    "/reset",
    response_model=SimulationResponse,
    summary="Reset Traffic Data",
    description="Clears all traffic data and resets detection engine.",
    status_code=status.HTTP_200_OK,
)
async def reset_traffic(
    aggregator: MetricsAggregator = Depends(get_aggregator),
) -> SimulationResponse:
    """Reset all traffic data and detection state."""
    try:
        aggregator.reset_all()

        logger.info("API: All traffic data and detection state reset")

        return SimulationResponse(
            success=True,
            message="All traffic data and detection state have been reset.",
            traffic_type=TrafficType.NORMAL,
            ips_generated=0,
            total_requests_generated=0,
            timestamp=timestamp_now(),
        )
    except Exception as exc:
        logger.exception("Failed to reset traffic data: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reset failed: {str(exc)}",
        )
