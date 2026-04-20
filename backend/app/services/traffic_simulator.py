"""
Traffic Simulation Service
----------------------------
Generates synthetic network traffic for both normal
usage patterns and DDoS attack scenarios.

Responsibilities:
    - Generate normal traffic (diverse IPs, low request count)
    - Generate attack traffic (few IPs, high request count)
    - Manage in-memory traffic store
    - Provide traffic reset capability
"""

from __future__ import annotations

import random
from typing import Dict, Tuple

from app.core.constants import TrafficConstants
from app.models.enums import TrafficType
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TrafficSimulator:
    """
    Simulates network traffic patterns for entropy analysis.

    The traffic store is an in-memory dictionary mapping
    IP addresses to their cumulative request counts.
    """

    def __init__(self) -> None:
        self._traffic: Dict[str, int] = {}
        self._generation_count: int = 0

    # ── Properties ───────────────────────────────────────────────

    @property
    def traffic(self) -> Dict[str, int]:
        """Current traffic distribution (read-only copy)."""
        return dict(self._traffic)

    @property
    def total_requests(self) -> int:
        """Total number of requests across all IPs."""
        return sum(self._traffic.values())

    @property
    def unique_ips(self) -> int:
        """Count of unique IP addresses in the store."""
        return len(self._traffic)

    # ── Normal Traffic ───────────────────────────────────────────

    async def generate_normal_traffic(self) -> Tuple[Dict[str, int], int]:
        """
        Generate normal traffic simulating legitimate users.

        Returns:
            Tuple of (generated_traffic_dict, total_new_requests)
        """
        num_ips = random.randint(
            TrafficConstants.NORMAL_IP_POOL_MIN,
            TrafficConstants.NORMAL_IP_POOL_MAX,
        )

        generated: Dict[str, int] = {}
        total_new = 0

        for _ in range(num_ips):
            ip = f"{TrafficConstants.NORMAL_IP_SUBNET}.{random.randint(1, 254)}"
            requests = random.randint(
                TrafficConstants.NORMAL_REQUESTS_PER_IP_MIN,
                TrafficConstants.NORMAL_REQUESTS_PER_IP_MAX,
            )
            generated[ip] = generated.get(ip, 0) + requests
            total_new += requests

        # Merge into traffic store
        for ip, count in generated.items():
            self._traffic[ip] = self._traffic.get(ip, 0) + count

        self._generation_count += 1
        logger.info(
            "Normal traffic generated: %d IPs, %d requests (batch #%d)",
            len(generated),
            total_new,
            self._generation_count,
        )

        return generated, total_new

    # ── Attack Traffic ───────────────────────────────────────────

    async def generate_attack_traffic(
        self,
        num_ips: int | None = None,
        requests_per_ip: int | None = None,
    ) -> Tuple[Dict[str, int], int]:
        """
        Generate DDoS attack traffic with concentrated requests.

        Args:
            num_ips: Number of attacking IPs (defaults to random within bounds)
            requests_per_ip: Requests per IP (defaults to random within bounds)

        Returns:
            Tuple of (generated_traffic_dict, total_new_requests)
        """
        ips = num_ips or random.randint(
            TrafficConstants.ATTACK_IP_POOL_MIN,
            TrafficConstants.ATTACK_IP_POOL_MAX,
        )
        rpi = requests_per_ip or random.randint(
            TrafficConstants.ATTACK_REQUESTS_PER_IP_MIN,
            TrafficConstants.ATTACK_REQUESTS_PER_IP_MAX,
        )

        generated: Dict[str, int] = {}
        total_new = 0

        for i in range(1, ips + 1):
            ip = f"{TrafficConstants.ATTACK_IP_SUBNET}.{i}"
            # Add slight variation per IP for realism
            actual_requests = rpi + random.randint(-20, 20)
            actual_requests = max(10, actual_requests)
            generated[ip] = actual_requests
            total_new += actual_requests

        # Merge into traffic store
        for ip, count in generated.items():
            self._traffic[ip] = self._traffic.get(ip, 0) + count

        self._generation_count += 1
        logger.warning(
            "⚠️  Attack traffic generated: %d IPs, %d total requests (batch #%d)",
            ips,
            total_new,
            self._generation_count,
        )

        return generated, total_new

    # ── Management ───────────────────────────────────────────────

    def reset(self) -> None:
        """Clear all traffic data and reset counters."""
        self._traffic.clear()
        self._generation_count = 0
        logger.info("🔄 Traffic store reset")

    def get_top_ips(self, n: int = 10) -> Dict[str, int]:
        """Return the top N IPs by request count."""
        sorted_items = sorted(
            self._traffic.items(), key=lambda x: x[1], reverse=True
        )
        return dict(sorted_items[:n])
