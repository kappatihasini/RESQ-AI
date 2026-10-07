from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DecisionStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    OVERRIDDEN = "OVERRIDDEN"
    REJECTED = "REJECTED"


class PlanStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    SUPERSEDED = "SUPERSEDED"


class AllocationDecision(BaseModel):
    id: str
    resource_id: str
    resource_code: str
    resource_type: str
    target_zone_id: str
    target_zone_name: str
    target_zone_triage: str
    distance_km: float
    eta_minutes: float
    matched_capabilities: List[str]
    capacity_contributed: int
    score_impact: float
    explanation_why_this_unit: str
    alternative_rejected: str
    constraints_satisfied: List[str]
    status: DecisionStatus = DecisionStatus.PROPOSED
    commander_override_reason: Optional[str] = None


class ResourcePlan(BaseModel):
    id: str
    plan_version: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: PlanStatus = PlanStatus.PROPOSED
    decisions: List[AllocationDecision] = []
    unassigned_resource_ids: List[str] = []
    unserved_zone_ids: List[str] = []
    total_estimated_lives_protected: int = 0
    total_avg_eta_minutes: float = 0.0
    strategic_summary: str
    is_replan: bool = False
    trigger_event: Optional[str] = None


class PlanDiffItem(BaseModel):
    resource_id: str
    resource_code: str
    old_zone_id: Optional[str]
    old_zone_name: Optional[str]
    new_zone_id: Optional[str]
    new_zone_name: Optional[str]
    old_eta: Optional[float]
    new_eta: Optional[float]
    change_type: str  # DIVERTED, RE-ROUTED, NEWLY_ASSIGNED, RELEASED
    reason: str


class PlanDiff(BaseModel):
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    old_plan_id: str
    new_plan_id: str
    trigger_event_title: str
    trigger_event_description: str
    changes: List[PlanDiffItem] = []
    diverted_count: int = 0
    newly_assigned_count: int = 0
    lives_risk_delta_explanation: str
    executive_diff_summary: str
