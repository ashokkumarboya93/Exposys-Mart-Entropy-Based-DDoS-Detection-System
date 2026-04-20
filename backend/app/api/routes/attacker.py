"""
Attacker Routes
-----------------
JWT-authenticated attack preset and burst simulation endpoints.
Only authenticated hacker users can launch attacks.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_hacker
from app.api.dependencies import get_aggregator
from app.models.schemas import CustomAttackRequest, AttackResponse
from app.services.attack_engine import AttackEngine
from app.services.metrics_aggregator import MetricsAggregator
from app.utils.helpers import timestamp_now
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/attack", tags=["Attacker"])


@router.get("/presets")
async def get_presets(_hacker: dict = Depends(require_hacker)):
    """Get available attack presets."""
    return {"success": True, "data": {"presets": AttackEngine.get_presets()}}


@router.post("/preset/{preset_type}", response_model=AttackResponse)
async def launch_preset(
    preset_type: str,
    db: Session = Depends(get_db),
    aggregator: MetricsAggregator = Depends(get_aggregator),
    _hacker: dict = Depends(require_hacker),
):
    """Launch a preset attack (spike, swarm, flood, etc.)."""
    try:
        result = await AttackEngine.launch_preset(
            preset_type=preset_type,
            db=db,
            aggregator=aggregator,
        )

        return AttackResponse(
            success=True,
            attack_id=result["attack_id"],
            preset_type=preset_type,
            message=f"{preset_type.title()} attack completed",
            num_ips=result["num_ips"],
            total_requests=result["total_requests"],
            waves_completed=result["waves_completed"],
            duration_ms=result["duration_ms"],
            ips_used=result["ips_used"],
            timestamp=timestamp_now(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Preset attack error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/custom", response_model=AttackResponse)
async def launch_custom(
    request: CustomAttackRequest,
    db: Session = Depends(get_db),
    aggregator: MetricsAggregator = Depends(get_aggregator),
    _hacker: dict = Depends(require_hacker),
):
    """Launch a custom attack with specified parameters."""
    try:
        result = await AttackEngine.launch_custom(
            db=db,
            aggregator=aggregator,
            num_ips=request.num_ips,
            requests_per_ip=request.requests_per_ip,
            waves=request.waves,
            wave_delay_ms=request.wave_delay_ms,
        )

        return AttackResponse(
            success=True,
            attack_id=result["attack_id"],
            preset_type="custom",
            message="Custom attack completed",
            num_ips=result["num_ips"],
            total_requests=result["total_requests"],
            waves_completed=result["waves_completed"],
            duration_ms=result["duration_ms"],
            ips_used=result["ips_used"],
            timestamp=timestamp_now(),
        )
    except Exception as exc:
        logger.exception("Custom attack error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/logs")
async def get_attack_logs(
    db: Session = Depends(get_db),
    _hacker: dict = Depends(require_hacker),
):
    """Get attack history log."""
    logs = AttackEngine.get_attack_logs(db)
    return {"success": True, "data": {"logs": logs, "total": len(logs)}}
