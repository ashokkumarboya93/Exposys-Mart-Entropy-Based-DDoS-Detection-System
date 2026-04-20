"""
Entropy Calculation Service
-----------------------------
Implements Shannon entropy computation for traffic
distribution analysis.

Responsibilities:
    - Calculate Shannon entropy from IP distribution
    - Compute maximum possible entropy
    - Normalize entropy to [0, 1] range
    - Return structured EntropyResult

Mathematical Foundation:
    H = -Σ (p_i * log2(p_i))
    where p_i = requests_from_IP_i / total_requests
"""

from __future__ import annotations

import math
from typing import Dict

from app.core.constants import DetectionConstants
from app.models.schemas import EntropyResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EntropyCalculator:
    """
    Computes Shannon entropy on network traffic distributions.

    High entropy → evenly distributed traffic (likely normal)
    Low entropy  → concentrated traffic (likely attack)
    """

    @staticmethod
    async def calculate(traffic: Dict[str, int]) -> EntropyResult:
        """
        Calculate Shannon entropy of the given traffic distribution.

        Args:
            traffic: Dictionary mapping IP → request count

        Returns:
            EntropyResult with entropy value, max entropy, and normalized value
        """
        if not traffic:
            logger.debug("Empty traffic — returning zero entropy")
            return EntropyResult(
                entropy_value=0.0,
                max_possible_entropy=0.0,
                normalized_entropy=0.0,
            )

        total_requests = sum(traffic.values())
        if total_requests == 0:
            return EntropyResult(
                entropy_value=0.0,
                max_possible_entropy=0.0,
                normalized_entropy=0.0,
            )

        num_ips = len(traffic)

        # ── Shannon Entropy: H = -Σ (p * log2(p)) ───────────────
        entropy = 0.0
        for ip, count in traffic.items():
            if count <= 0:
                continue
            probability = count / total_requests
            entropy -= probability * math.log(probability, DetectionConstants.LOG_BASE)

        # ── Maximum Possible Entropy ─────────────────────────────
        max_entropy = (
            math.log(num_ips, DetectionConstants.LOG_BASE) if num_ips > 1 else 0.0
        )

        # ── Normalized Entropy [0, 1] ────────────────────────────
        normalized = entropy / max_entropy if max_entropy > 0 else 0.0
        normalized = min(1.0, max(0.0, normalized))  # Clamp

        result = EntropyResult(
            entropy_value=round(entropy, 6),
            max_possible_entropy=round(max_entropy, 6),
            normalized_entropy=round(normalized, 6),
        )

        logger.info(
            "Entropy calculated: H=%.4f, H_max=%.4f, normalized=%.4f (%d IPs, %d requests)",
            entropy,
            max_entropy,
            normalized,
            num_ips,
            total_requests,
        )

        return result
