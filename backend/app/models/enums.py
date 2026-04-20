"""
Enumeration Types
------------------
Strongly-typed enumerations used across the application.
"""

from __future__ import annotations

from enum import Enum


class TrafficType(str, Enum):
    NORMAL = "normal"
    ATTACK = "attack"
    MIXED = "mixed"


class DetectionStatus(str, Enum):
    NORMAL = "NORMAL"
    DDOS_ATTACK = "DDOS_ATTACK"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class Severity(str, Enum):
    SAFE = "safe"
    WARNING = "warning"
    CRITICAL = "critical"


class AttackPresetType(str, Enum):
    SPIKE = "spike"
    SWARM = "swarm"
    FLOOD = "flood"
    CUSTOM = "custom"


class StoreAction(str, Enum):
    PAGEVIEW = "pageview"
    CLICK = "click"
    SEARCH = "search"
    ADD_TO_CART = "add_to_cart"
    REMOVE_FROM_CART = "remove_from_cart"
    CHECKOUT = "checkout"
    CATEGORY_FILTER = "category_filter"
