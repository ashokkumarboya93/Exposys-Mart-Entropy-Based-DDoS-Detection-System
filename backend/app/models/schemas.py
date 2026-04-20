"""
Pydantic Schemas (Data Transfer Objects)
-----------------------------------------
All request/response schemas for the API layer.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.enums import DetectionStatus, Severity, TrafficType, AttackPresetType, StoreAction


# ═══════════════════════════════════════════════════════════════════
#  REQUEST SCHEMAS
# ═══════════════════════════════════════════════════════════════════

class AttackSimulationRequest(BaseModel):
    num_ips: int = Field(default=3, ge=1, le=50)
    requests_per_ip: int = Field(default=200, ge=10, le=10000)

    model_config = {
        "json_schema_extra": {
            "examples": [{"num_ips": 3, "requests_per_ip": 200}]
        }
    }


class StoreTrackRequest(BaseModel):
    session_id: str = Field(default="", description="Browser session ID")
    page: str = Field(default="homepage", description="Page being viewed")
    action: StoreAction = Field(default=StoreAction.PAGEVIEW)
    product_id: Optional[int] = Field(default=None)
    search_query: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None)


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class CustomAttackRequest(BaseModel):
    num_ips: int = Field(default=5, ge=1, le=50)
    requests_per_ip: int = Field(default=500, ge=10, le=10000)
    waves: int = Field(default=1, ge=1, le=10)
    wave_delay_ms: int = Field(default=0, ge=0, le=5000)


# ═══════════════════════════════════════════════════════════════════
#  INTERNAL DATA MODELS
# ═══════════════════════════════════════════════════════════════════

class TrafficData(BaseModel):
    distribution: Dict[str, int] = Field(default_factory=dict)
    total_requests: int = Field(default=0, ge=0)
    unique_ips: int = Field(default=0, ge=0)
    traffic_type: TrafficType = Field(default=TrafficType.NORMAL)


class EntropyResult(BaseModel):
    entropy_value: float = Field(default=0.0, ge=0.0)
    max_possible_entropy: float = Field(default=0.0, ge=0.0)
    normalized_entropy: float = Field(default=0.0, ge=0.0, le=1.0)


class DetectionResult(BaseModel):
    status: DetectionStatus = Field(default=DetectionStatus.INSUFFICIENT_DATA)
    severity: Severity = Field(default=Severity.SAFE)
    entropy: EntropyResult = Field(default_factory=EntropyResult)
    baseline_entropy: Optional[float] = None
    threshold: Optional[float] = None
    message: str = Field(default="Awaiting sufficient data for analysis.")
    suspicious_ips: List[Dict[str, object]] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════
#  RESPONSE SCHEMAS
# ═══════════════════════════════════════════════════════════════════

class SimulationResponse(BaseModel):
    success: bool = Field(default=True)
    message: str
    traffic_type: TrafficType
    ips_generated: int = Field(ge=0)
    total_requests_generated: int = Field(ge=0)
    timestamp: str


class MetricsResponse(BaseModel):
    total_requests: int = Field(default=0, ge=0)
    unique_ips: int = Field(default=0, ge=0)
    entropy: float = Field(default=0.0, ge=0.0)
    normalized_entropy: float = Field(default=0.0, ge=0.0, le=1.0)
    status: DetectionStatus = Field(default=DetectionStatus.INSUFFICIENT_DATA)
    severity: Severity = Field(default=Severity.SAFE)
    baseline_entropy: Optional[float] = None
    threshold: Optional[float] = None
    message: str = Field(default="System initializing...")
    traffic_distribution: List[Dict[str, object]] = Field(default_factory=list)
    suspicious_ips: List[Dict[str, object]] = Field(default_factory=list)
    timestamp: str = Field(default="")


class HealthResponse(BaseModel):
    status: str = Field(default="healthy")
    version: str
    environment: str
    uptime_seconds: Optional[float] = None


class StoreTrackResponse(BaseModel):
    success: bool = True
    message: str = ""
    session_id: str = ""
    traffic_generated: int = 0


class AdminLoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    message: str = ""


class AdminAnalyticsResponse(BaseModel):
    total_requests: int = 0
    active_shoppers: int = 0
    unique_ips: int = 0
    entropy_score: float = 0.0
    normalized_entropy: float = 0.0
    attack_confidence: float = 0.0
    status: str = "NORMAL"
    severity: str = "safe"
    baseline_entropy: Optional[float] = None
    threshold: Optional[float] = None
    message: str = ""
    suspicious_ips: List[Dict] = Field(default_factory=list)
    traffic_distribution: List[Dict] = Field(default_factory=list)
    entropy_history: List[Dict] = Field(default_factory=list)
    recent_sessions: List[Dict] = Field(default_factory=list)
    recent_requests: List[Dict] = Field(default_factory=list)
    attack_events: List[Dict] = Field(default_factory=list)
    traffic_timeline: List[Dict] = Field(default_factory=list)
    top_attacked_endpoints: List[Dict] = Field(default_factory=list)
    normal_vs_attack: Dict = Field(default_factory=dict)
    timestamp: str = ""


class AttackResponse(BaseModel):
    success: bool = True
    attack_id: str = ""
    preset_type: str = ""
    message: str = ""
    num_ips: int = 0
    total_requests: int = 0
    waves_completed: int = 0
    duration_ms: int = 0
    ips_used: List[str] = Field(default_factory=list)
    timestamp: str = ""


class AttackLogEntry(BaseModel):
    attack_id: str
    timestamp: str
    preset_type: str
    num_ips: int
    requests_per_ip: int
    total_requests: int
    status: str
    duration_ms: int
