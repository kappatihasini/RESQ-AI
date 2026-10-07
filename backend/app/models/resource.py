from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ResourceType(str, Enum):
    NDRF_RESCUE_BOAT = "NDRF_RESCUE_BOAT"
    AMPHIBIOUS_ATV = "AMPHIBIOUS_ATV"
    ALS_AMBULANCE = "ALS_AMBULANCE"
    MEDICAL_EVAC_TEAM = "MEDICAL_EVAC_TEAM"
    DRONE_RECON = "DRONE_RECON"
    HEAVY_PUMP_SUPPLY = "HEAVY_PUMP_SUPPLY"


class ResourceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    COMMITTED = "COMMITTED"
    MAINTENANCE = "MAINTENANCE"


class EmergencyResource(BaseModel):
    id: str
    code: str  # e.g., NDRF-B01, AMB-04
    name: str
    type: ResourceType
    capabilities: List[str]  # e.g. ["FLOOD_EVAC", "AMPHIBIOUS", "DEEP_WATER"]
    base_station: str
    current_lat: float
    current_lon: float
    capacity_persons: int = 4
    speed_kmh: float = 30.0
    status: ResourceStatus = ResourceStatus.AVAILABLE
    current_assigned_zone_id: Optional[str] = None
    estimated_arrival_minutes: Optional[float] = None
    fuel_or_battery_percent: int = 100
    is_amphibious_or_air: bool = False
