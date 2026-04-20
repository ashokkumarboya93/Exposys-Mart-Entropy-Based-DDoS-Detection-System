"""
DDoS Detection Engine
-----------------------
Threshold-based detection using entropy analysis.

Responsibilities:
    - Maintain rolling baseline of normal entropy
    - Compare current entropy against threshold
    - Classify traffic as normal or attack
    - Identify suspicious IP addresses
    - Assign severity levels

Detection Logic:
    IF current_entropy < (baseline_entropy * threshold_ratio)
    → DDOS_ATTACK
    ELSE
    → NORMAL
"""

from __future__ import annotations

from collections import deque
from typing import Dict, List

from app.core.config import settings
from app.core.constants import DetectionConstants
from app.models.enums import DetectionStatus, Severity
from app.models.schemas import DetectionResult, EntropyResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DetectionEngine:
    """
    Entropy-based DDoS detection engine with adaptive baseline.

    Maintains a rolling window of entropy samples to compute
    a dynamic baseline for threshold comparison.
    """

    def __init__(self) -> None:
        self._baseline_samples: deque[float] = deque(
            maxlen=settings.BASELINE_SAMPLE_COUNT
        )
        self._baseline_entropy: float | None = None
        self._detection_count: int = 0

    # ── Properties ───────────────────────────────────────────────

    @property
    def baseline_entropy(self) -> float | None:
        """Current computed baseline entropy value."""
        return self._baseline_entropy

    @property
    def threshold(self) -> float | None:
        """Current detection threshold."""
        if self._baseline_entropy is None:
            return None
        return round(
            self._baseline_entropy * settings.ENTROPY_THRESHOLD_RATIO, 6
        )

    @property
    def has_baseline(self) -> bool:
        """Whether enough samples exist to establish a baseline."""
        return len(self._baseline_samples) >= 3

    # ── Core Detection ───────────────────────────────────────────

    async def analyze(
        self,
        entropy_result: EntropyResult,
        traffic: Dict[str, int],
    ) -> DetectionResult:
        """
        Analyze traffic for DDoS patterns using entropy comparison.

        Args:
            entropy_result: Computed entropy of current traffic
            traffic: Current traffic distribution

        Returns:
            DetectionResult with status, severity, and details

        Raises:
            Never — all exceptions are caught and returned as
            INSUFFICIENT_DATA with error messages.
        """
        try:
            return await self._perform_analysis(entropy_result, traffic)
        except Exception as exc:
            logger.exception("Detection engine error: %s", exc)
            return DetectionResult(
                status=DetectionStatus.INSUFFICIENT_DATA,
                severity=Severity.SAFE,
                entropy=entropy_result,
                message=f"Detection engine error: {str(exc)}",
            )

    async def _perform_analysis(
        self,
        entropy_result: EntropyResult,
        traffic: Dict[str, int],
    ) -> DetectionResult:
        """Internal analysis logic — separated for clean exception handling."""
        self._detection_count += 1
        current_entropy = entropy_result.entropy_value

        # ── Insufficient Data ────────────────────────────────────
        if not traffic or len(traffic) < 2:
            return DetectionResult(
                status=DetectionStatus.INSUFFICIENT_DATA,
                severity=Severity.SAFE,
                entropy=entropy_result,
                message="Insufficient traffic data for analysis. Need at least 2 unique IPs.",
            )

        # ── Update Baseline (only with high-entropy samples) ─────
        if not self.has_baseline:
            self._baseline_samples.append(current_entropy)
            self._update_baseline()

            if not self.has_baseline:
                return DetectionResult(
                    status=DetectionStatus.INSUFFICIENT_DATA,
                    severity=Severity.SAFE,
                    entropy=entropy_result,
                    baseline_entropy=self._baseline_entropy,
                    message=(
                        f"Building baseline: {len(self._baseline_samples)}"
                        f"/{settings.BASELINE_SAMPLE_COUNT} samples collected."
                    ),
                )

        # ── Threshold Comparison ─────────────────────────────────
        current_threshold = self.threshold
        suspicious_ips = self._identify_suspicious_ips(traffic)

        if current_entropy < current_threshold:
            # ── DDoS Attack Detected ─────────────────────────────
            severity = self._classify_severity(current_entropy, current_threshold)

            logger.critical(
                "🚨 DDOS ATTACK DETECTED! entropy=%.4f < threshold=%.4f "
                "(baseline=%.4f, severity=%s, suspicious_ips=%d)",
                current_entropy,
                current_threshold,
                self._baseline_entropy,
                severity.value,
                len(suspicious_ips),
            )

            return DetectionResult(
                status=DetectionStatus.DDOS_ATTACK,
                severity=severity,
                entropy=entropy_result,
                baseline_entropy=self._baseline_entropy,
                threshold=current_threshold,
                message=(
                    f"🚨 DDoS attack detected! Entropy ({current_entropy:.4f}) "
                    f"dropped below threshold ({current_threshold:.4f}). "
                    f"{len(suspicious_ips)} suspicious IP(s) identified."
                ),
                suspicious_ips=suspicious_ips,
            )

        # ── Normal Traffic ───────────────────────────────────────
        # Update baseline with normal samples
        if entropy_result.normalized_entropy > 0.6:
            self._baseline_samples.append(current_entropy)
            self._update_baseline()

        logger.info(
            "✅ Traffic normal — entropy=%.4f, threshold=%.4f (detection #%d)",
            current_entropy,
            current_threshold,
            self._detection_count,
        )

        return DetectionResult(
            status=DetectionStatus.NORMAL,
            severity=Severity.SAFE,
            entropy=entropy_result,
            baseline_entropy=self._baseline_entropy,
            threshold=current_threshold,
            message=(
                f"Traffic appears normal. Entropy ({current_entropy:.4f}) "
                f"is above threshold ({current_threshold:.4f})."
            ),
            suspicious_ips=[],
        )

    # ── Private Helpers ──────────────────────────────────────────

    def _update_baseline(self) -> None:
        """Recalculate baseline as the average of collected samples."""
        if self._baseline_samples:
            self._baseline_entropy = round(
                sum(self._baseline_samples) / len(self._baseline_samples), 6
            )

    def _identify_suspicious_ips(
        self,
        traffic: Dict[str, int],
        percentile: float = 0.9,
    ) -> List[Dict[str, object]]:
        """
        Identify IPs sending disproportionately high traffic.

        An IP is suspicious if its request count exceeds the
        90th percentile of all request counts.
        """
        if not traffic:
            return []

        counts = sorted(traffic.values())
        threshold_index = int(len(counts) * percentile)
        threshold_index = min(threshold_index, len(counts) - 1)
        count_threshold = counts[threshold_index]

        total = sum(traffic.values())
        suspicious = []

        for ip, count in traffic.items():
            if count >= count_threshold and count > 10:
                suspicious.append(
                    {
                        "ip": ip,
                        "requests": count,
                        "percentage": round((count / total) * 100, 2) if total else 0,
                    }
                )

        return sorted(suspicious, key=lambda x: x["requests"], reverse=True)

    def _classify_severity(
        self,
        current_entropy: float,
        threshold: float,
    ) -> Severity:
        """
        Classify attack severity based on how far entropy dropped
        below the threshold.
        """
        if threshold == 0:
            return Severity.CRITICAL

        ratio = current_entropy / threshold

        if ratio < 0.3:
            return Severity.CRITICAL
        elif ratio < 0.7:
            return Severity.CRITICAL
        else:
            return Severity.WARNING

    # ── Management ───────────────────────────────────────────────

    def reset(self) -> None:
        """Reset detection engine state."""
        self._baseline_samples.clear()
        self._baseline_entropy = None
        self._detection_count = 0
        logger.info("🔄 Detection engine reset")
