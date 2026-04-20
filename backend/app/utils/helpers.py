"""
Helper Utilities
-----------------
General-purpose utility functions used across the application.

Responsibilities:
    - IP distribution formatting
    - Timestamp generation
    - Data transformation helpers
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List


def timestamp_now() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def format_ip_distribution(
    traffic: Dict[str, int],
    top_n: int = 10,
) -> List[Dict[str, object]]:
    """
    Format raw traffic dictionary into a sorted list of
    IP distribution records, limited to top_n entries.

    Args:
        traffic: Dictionary mapping IP → request count
        top_n: Maximum entries to return

    Returns:
        Sorted list of dicts with 'ip', 'requests', 'percentage' keys
    """
    total = sum(traffic.values()) if traffic else 0
    if total == 0:
        return []

    sorted_ips = sorted(traffic.items(), key=lambda x: x[1], reverse=True)

    return [
        {
            "ip": ip,
            "requests": count,
            "percentage": round((count / total) * 100, 2),
        }
        for ip, count in sorted_ips[:top_n]
    ]


def calculate_percentage(part: int, whole: int) -> float:
    """Safe percentage calculation avoiding division by zero."""
    if whole == 0:
        return 0.0
    return round((part / whole) * 100, 2)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max bounds."""
    return max(min_val, min(value, max_val))
