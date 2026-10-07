from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class SourceType(str, Enum):
    CITIZEN_SOS = "CITIZEN_SOS"
    FIELD_DRONE = "FIELD_DRONE"
    IOT_SENSOR = "IOT_SENSOR"
    EOC_DISPATCH = "EOC_DISPATCH"


class RoadStatus(str, Enum):
    PASSABLE = "PASSABLE"
    SLOW_TRAFFIC = "SLOW_TRAFFIC"
    WATERLOGGED = "WATERLOGGED"
    BLOCKED = "BLOCKED"
    SUBMERGED = "SUBMERGED"
    COLLAPSED = "COLLAPSED"


class ConflictType(str, Enum):
    CASUALTY_DISCREPANCY = "CASUALTY_DISCREPANCY"
    ROAD_STATUS_CONTRADICTION = "ROAD_STATUS_CONTRADICTION"
    WATER_DEPTH_MISMATCH = "WATER_DEPTH_MISMATCH"
    URGENCY_INCONSISTENCY = "URGENCY_INCONSISTENCY"


class RawEvidence(BaseModel):
    id: str
    source: SourceType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    latitude: float
    longitude: float
    description: str
    reported_casualties: int = 0
    road_status: RoadStatus = RoadStatus.PASSABLE
    water_depth_m: float = 0.0
    hazard_type: str = "FLOOD"
    raw_payload: Optional[Dict[str, Any]] = None


class Conflict(BaseModel):
    id: str
    conflict_type: ConflictType
    evidence_ids: List[str]
    description: str
    severity: str = "MEDIUM"  # LOW, MEDIUM, CRITICAL
    resolution_status: str = "FLAGGED"  # FLAGGED, AUTO_RESOLVED, COMMANDER_RESOLVED
    resolution_note: Optional[str] = None


class EvidenceConfidence(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    source_weight_factor: float
    cross_validation_count: int
    freshness_factor: float
    conflict_penalty: float
    rationale: str


class Incident(BaseModel):
    id: str
    cluster_id: str
    title: str
    hazard_type: str
    latitude: float
    longitude: float
    address_or_landmark: str
    aggregated_casualties: int
    casualty_range: str  # e.g., "12 - 18 verified"
    verified_road_status: RoadStatus
    verified_water_depth_m: float
    confidence: EvidenceConfidence
    conflicts: List[Conflict] = []
    evidence_list: List[RawEvidence] = []
    zone_id: Optional[str] = None
    status: str = "ACTIVE"  # ACTIVE, CONTAINED, RESOLVED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
