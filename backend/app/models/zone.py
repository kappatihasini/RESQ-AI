from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TriageLevel(str, Enum):
    CRITICAL_P1 = "CRITICAL_P1"  # Score >= 80
    HIGH_P2 = "HIGH_P2"          # Score 60 - 79
    MEDIUM_P3 = "MEDIUM_P3"      # Score 40 - 59
    LOW_P4 = "LOW_P4"            # Score < 40


class ScoreBreakdown(BaseModel):
    urgency_raw: float = Field(..., ge=1.0, le=10.0)
    urgency_weighted: float
    severity_raw: float = Field(..., ge=1.0, le=10.0)
    severity_weighted: float
    vulnerability_raw: float = Field(..., ge=1.0, le=5.0)
    vulnerability_weighted: float
    accessibility_factor: float = Field(..., ge=0.5, le=1.0)
    evidence_confidence: float = Field(..., ge=0.0, le=1.0)
    calculated_formula: str
    explanation: str


class CriticalZone(BaseModel):
    id: str
    name: str
    code: str  # e.g., ZONE-ALPHA
    center_lat: float
    center_lon: float
    radius_meters: float = 500.0
    incident_ids: List[str] = []
    
    # Raw formula inputs
    urgency: float = Field(default=5.0, ge=1.0, le=10.0)       # Time-to-criticality
    severity: float = Field(default=5.0, ge=1.0, le=10.0)      # Casualties & physical scale
    vulnerability: float = Field(default=2.5, ge=1.0, le=5.0)  # Demographics (ICU, elderly, children)
    accessibility_factor: float = Field(default=1.0, ge=0.5, le=1.0) # 1.0 = clear, 0.5 = heavily blocked
    
    # Calculated outputs
    priority_score: float = Field(default=0.0, ge=0.0, le=100.0)
    triage_level: TriageLevel = TriageLevel.MEDIUM_P3
    score_breakdown: Optional[ScoreBreakdown] = None
    
    # Zone specifics
    required_capabilities: List[str] = []
    estimated_stranded_count: int = 0
    water_level_m: float = 0.0
    power_status: str = "NORMAL"  # NORMAL, ON_BACKUP, FAILING, OUT
    status: str = "TRIAGED"        # TRIAGED, ALLOCATED, DISPATCHED, STABILIZED
