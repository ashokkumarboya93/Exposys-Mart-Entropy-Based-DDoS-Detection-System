"""
Attack Engine Service
-----------------------
Handles attack presets, async burst waves, rotating IP simulation,
and attack event persistence.
"""

from __future__ import annotations

import asyncio
import random
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.constants import AttackPresets, TrafficConstants
from app.models.db_models import AttackEvent, TrafficEvent, SuspiciousIP
from app.utils.logger import get_logger

logger = get_logger(__name__)


# Pool of realistic bot subnets for rotating IPs
BOT_SUBNETS = [
    "10.0.0", "10.0.1", "10.0.2", "10.1.0", "10.2.0",
    "172.16.0", "172.16.1", "172.17.0", "172.18.0",
    "192.0.2", "198.51.100", "203.0.113",
]


class AttackEngine:
    """
    Manages DDoS attack simulation with presets, burst waves,
    and rotating bot IPs.
    """

    @staticmethod
    def get_presets() -> Dict:
        return AttackPresets.PRESETS

    @staticmethod
    async def launch_preset(
        preset_type: str,
        db: Session,
        aggregator,
    ) -> Dict:
        """Launch a preset attack and persist to DB."""
        preset = AttackPresets.PRESETS.get(preset_type)
        if not preset:
            raise ValueError(f"Unknown preset: {preset_type}")

        return await AttackEngine._execute_attack(
            db=db,
            aggregator=aggregator,
            preset_type=preset_type,
            num_ips=preset["num_ips"],
            requests_per_ip=preset["requests_per_ip"],
            waves=preset["waves"],
            wave_delay_ms=preset["wave_delay_ms"],
        )

    @staticmethod
    async def launch_custom(
        db: Session,
        aggregator,
        num_ips: int,
        requests_per_ip: int,
        waves: int = 1,
        wave_delay_ms: int = 0,
    ) -> Dict:
        """Launch a custom attack."""
        return await AttackEngine._execute_attack(
            db=db,
            aggregator=aggregator,
            preset_type="custom",
            num_ips=num_ips,
            requests_per_ip=requests_per_ip,
            waves=waves,
            wave_delay_ms=wave_delay_ms,
        )

    @staticmethod
    async def _execute_attack(
        db: Session,
        aggregator,
        preset_type: str,
        num_ips: int,
        requests_per_ip: int,
        waves: int,
        wave_delay_ms: int,
    ) -> Dict:
        """Core attack execution with wave support and rotating IPs."""
        attack_id = str(uuid.uuid4())
        start_time = time.time()
        all_ips_used: set[str] = set()
        # Session-level cache to avoid duplicate inserts when autoflush is disabled.
        suspicious_cache: dict[str, SuspiciousIP] = {}
        total_requests = 0

        for wave in range(waves):
            # Rotate subnet per wave for realism
            subnet = random.choice(BOT_SUBNETS)
            # Keep wave IPs unique to prevent accidental duplicate UNIQUE-key inserts.
            host_octets = random.sample(range(1, 255), k=num_ips)
            wave_ips = [f"{subnet}.{host}" for host in host_octets]
            wave_total = 0

            for ip in wave_ips:
                actual_requests = requests_per_ip + random.randint(-20, 20)
                actual_requests = max(10, actual_requests)

                wave_total += actual_requests

                # Persist traffic event
                event = TrafficEvent(
                    ip_address=ip,
                    endpoint="/store/homepage",
                    method="GET",
                    traffic_type="attack",
                    session_id=f"bot-{attack_id[:8]}",
                    action="bot_request",
                    request_count=actual_requests,
                )
                db.add(event)

                # Update suspicious IP tracking
                sus = suspicious_cache.get(ip)
                if not sus:
                    sus = db.query(SuspiciousIP).filter(
                        SuspiciousIP.ip_address == ip
                    ).first()

                if sus:
                    sus.total_requests += actual_requests
                    sus.last_seen = datetime.utcnow()
                    sus.risk_score = min(100.0, sus.risk_score + 10.0)
                else:
                    sus = SuspiciousIP(
                        ip_address=ip,
                        total_requests=actual_requests,
                        risk_score=50.0,
                    )
                    db.add(sus)
                suspicious_cache[ip] = sus

            # Also feed into the in-memory traffic simulator for entropy calculation
            generated = {}
            for ip in wave_ips:
                rpi = requests_per_ip + random.randint(-20, 20)
                rpi = max(10, rpi)
                generated[ip] = rpi

            for ip, count in generated.items():
                aggregator.traffic_simulator._traffic[ip] = (
                    aggregator.traffic_simulator._traffic.get(ip, 0) + count
                )

            all_ips_used.update(wave_ips)
            total_requests += wave_total

            # Wave delay
            if wave < waves - 1 and wave_delay_ms > 0:
                await asyncio.sleep(wave_delay_ms / 1000.0)

        duration_ms = int((time.time() - start_time) * 1000)

        # Persist attack event
        attack = AttackEvent(
            attack_id=attack_id,
            preset_type=preset_type,
            num_ips=num_ips,
            requests_per_ip=requests_per_ip,
            total_requests=total_requests,
            status="completed",
            duration_ms=duration_ms,
            ips_used=sorted(all_ips_used),
        )
        db.add(attack)
        db.commit()

        logger.warning(
            "⚠️ Attack executed: type=%s, ips=%d, total=%d, waves=%d, duration=%dms",
            preset_type, num_ips, total_requests, waves, duration_ms,
        )

        return {
            "attack_id": attack_id,
            "preset_type": preset_type,
            "num_ips": num_ips,
            "total_requests": total_requests,
            "waves_completed": waves,
            "duration_ms": duration_ms,
            "ips_used": sorted(all_ips_used),
        }

    @staticmethod
    def get_attack_logs(db: Session, limit: int = 50) -> List[Dict]:
        """Get recent attack history."""
        attacks = db.query(AttackEvent).order_by(
            AttackEvent.timestamp.desc()
        ).limit(limit).all()

        return [
            {
                "attack_id": a.attack_id,
                "timestamp": a.timestamp.isoformat() if a.timestamp else "",
                "preset_type": a.preset_type,
                "num_ips": a.num_ips,
                "requests_per_ip": a.requests_per_ip,
                "total_requests": a.total_requests,
                "status": a.status,
                "duration_ms": a.duration_ms,
            }
            for a in attacks
        ]
