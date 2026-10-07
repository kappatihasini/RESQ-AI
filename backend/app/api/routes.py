from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from ..simulation.simulator import simulator
from ..models.incident import Incident, Conflict, RawEvidence
from ..models.zone import CriticalZone
from ..models.resource import EmergencyResource
from ..models.plan import ResourcePlan, PlanDiff

router = APIRouter(prefix="/api")


class ApprovalRequest(BaseModel):
    commander_name: str = "Commander V. Sharma"
    notes: Optional[str] = "Approved after reviewing trade-offs and capability allocation."


class OverrideRequest(BaseModel):
    decision_id: str
    new_resource_id: str
    commander_name: str = "Commander V. Sharma"
    reason: str


class CustomEvidenceRequest(BaseModel):
    source: str = "CITIZEN_SOS"
    latitude: float
    longitude: float
    description: str
    reported_casualties: int = 5
    road_status: str = "WATERLOGGED"
    water_depth_m: float = 0.8
    hazard_type: str = "FLOOD"


@router.get("/state")
def get_full_state():
    """Returns complete synchronized EOC state."""
    return simulator.get_full_state()


@router.get("/incidents", response_model=List[Incident])
def get_incidents():
    """Returns verified incidents with cross-validated evidence."""
    return simulator.incidents


@router.get("/zones", response_model=List[CriticalZone])
def get_zones():
    """Returns prioritized critical zones with explainable score breakdown."""
    return simulator.zones


@router.get("/resources", response_model=List[EmergencyResource])
def get_resources():
    """Returns emergency resource fleet status."""
    return simulator.resources


@router.get("/plan", response_model=ResourcePlan)
def get_current_plan():
    """Returns current active or proposed allocation plan."""
    return simulator.current_plan


@router.get("/plan/diff")
def get_latest_diff():
    """Returns latest Old Plan vs New Plan diff if a replan occurred."""
    if not simulator.latest_diff:
        return {"diff_available": False, "message": "No replanning diff active. Currently on baseline plan."}
    return {"diff_available": True, "diff": simulator.latest_diff}


@router.post("/simulation/act2/shock")
def trigger_act_2():
    """Triggers Act II: Bhatia Bridge Collapse + Chemical Corridor Flash Breach & Auto-Replan."""
    result = simulator.trigger_act_2_shock()
    return result


@router.post("/simulation/act3/approve")
def trigger_act_3(req: ApprovalRequest):
    """Triggers Act III: Human Commander Authorization and Dispatch."""
    result = simulator.trigger_act_3_approval_and_dispatch(
        commander_name=req.commander_name, notes=req.notes
    )
    return result


@router.post("/simulation/reset")
def reset_simulation():
    """Resets the simulation to fresh Act I state."""
    simulator.reset()
    return {"status": "RESET_SUCCESS", "message": "Simulation reset to Act I baseline."}


@router.post("/plan/override")
def override_decision(req: OverrideRequest):
    """Allows Human Commander to manually override a unit assignment."""
    try:
        result = simulator.override_decision(
            decision_id=req.decision_id,
            new_resource_id=req.new_resource_id,
            commander_name=req.commander_name,
            reason=req.reason,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
