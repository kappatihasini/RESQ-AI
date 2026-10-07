from typing import List, Dict, Any
from datetime import datetime

from ..models.incident import RawEvidence, SourceType, RoadStatus
from ..models.zone import CriticalZone, TriageLevel
from ..models.resource import EmergencyResource, ResourceType, ResourceStatus


def get_seed_raw_evidence() -> List[RawEvidence]:
    """
    Returns realistic seeded multi-source emergency evidence for Act I.
    Includes citizen SOS, field drone pings, IoT flood sensors, and EOC dispatches.
    """
    return [
        # Sector 1: Metro General Hospital (Cluster 1)
        RawEvidence(
            id="EVID-001",
            source=SourceType.CITIZEN_SOS,
            latitude=13.0825,
            longitude=80.2705,
            description="Basement flooded at Metro Hospital! Backup ICU generators underwater, power flickering.",
            reported_casualties=35,
            road_status=RoadStatus.SUBMERGED,
            water_depth_m=1.3,
            hazard_type="FLOOD",
        ),
        RawEvidence(
            id="EVID-002",
            source=SourceType.IOT_SENSOR,
            latitude=13.0828,
            longitude=80.2708,
            description="Telemetry Sensor #SEN-HOSP-09: Water level 1.45m. Surge rate +0.2m/hr.",
            reported_casualties=0,
            road_status=RoadStatus.SUBMERGED,
            water_depth_m=1.45,
            hazard_type="FLOOD",
        ),
        RawEvidence(
            id="EVID-003",
            source=SourceType.FIELD_DRONE,
            latitude=13.0826,
            longitude=80.2706,
            description="Drone Recon D-01: Confirmed ground floor inundation; 40+ patients trapped on 1st floor ramp.",
            reported_casualties=42,
            road_status=RoadStatus.SUBMERGED,
            water_depth_m=1.4,
            hazard_type="FLOOD",
        ),
        RawEvidence(
            id="EVID-004",
            source=SourceType.CITIZEN_SOS,
            latitude=13.0831,
            longitude=80.2712,
            description="Hospital ambulance bay entrance still reachable by high-axle trucks according to security guard.",
            reported_casualties=10,
            road_status=RoadStatus.PASSABLE,  # Direct conflict with sensor/drone!
            water_depth_m=0.3,
            hazard_type="FLOOD",
        ),

        # Sector 2: Coastal Residential Ward 4 (Cluster 2)
        RawEvidence(
            id="EVID-005",
            source=SourceType.CITIZEN_SOS,
            latitude=13.0910,
            longitude=80.2815,
            description="Canal wall overflowed! 6 houses submerged up to roof level. Children and elderly on terrace.",
            reported_casualties=28,
            road_status=RoadStatus.WATERLOGGED,
            water_depth_m=1.1,
            hazard_type="FLOOD",
        ),
        RawEvidence(
            id="EVID-006",
            source=SourceType.FIELD_DRONE,
            latitude=13.0915,
            longitude=80.2818,
            description="Drone Recon D-02: Visual confirms 24 individuals waving orange flags on terrace in Ward 4.",
            reported_casualties=24,
            road_status=RoadStatus.WATERLOGGED,
            water_depth_m=1.0,
            hazard_type="FLOOD",
        ),

        # Sector 3: Metro Transit Underpass (Cluster 3)
        RawEvidence(
            id="EVID-007",
            source=SourceType.EOC_DISPATCH,
            latitude=13.0760,
            longitude=80.2620,
            description="Traffic Police Dispatch: City Bus stalled in flooded underpass. 16 passengers trapped inside.",
            reported_casualties=16,
            road_status=RoadStatus.BLOCKED,
            water_depth_m=0.9,
            hazard_type="FLOOD",
        ),
        RawEvidence(
            id="EVID-008",
            source=SourceType.IOT_SENSOR,
            latitude=13.0762,
            longitude=80.2623,
            description="Underpass Depth Gauge #U-04: Water depth 0.95m. Flow velocity moderate.",
            reported_casualties=0,
            road_status=RoadStatus.BLOCKED,
            water_depth_m=0.95,
            hazard_type="FLOOD",
        ),

        # Sector 4: Riverside Shelter (Cluster 4)
        RawEvidence(
            id="EVID-009",
            source=SourceType.EOC_DISPATCH,
            latitude=13.0700,
            longitude=80.2550,
            description="Government Higher Sec School Shelter: 35 evacuees housed. Food and potable water supplies running low.",
            reported_casualties=0,
            road_status=RoadStatus.PASSABLE,
            water_depth_m=0.15,
            hazard_type="RELIEF_LOGISTICS",
        ),
    ]


def get_seed_zones() -> List[CriticalZone]:
    """Returns initial baseline zones for the EOC scenario."""
    return [
        CriticalZone(
            id="ZONE-01",
            code="ZONE-ALPHA",
            name="Metro General Hospital & Trauma Centre",
            center_lat=13.0827,
            center_lon=80.2707,
            radius_meters=600.0,
            urgency=9.5,
            severity=9.2,
            vulnerability=4.8,  # ICU & oxygen dependents
            accessibility_factor=0.60,
            estimated_stranded_count=42,
            water_level_m=1.4,
            power_status="FAILING",
            status="TRIAGED",
        ),
        CriticalZone(
            id="ZONE-02",
            code="ZONE-BRAVO",
            name="South Coast Residential Ward 4",
            center_lat=13.0912,
            center_lon=80.2816,
            radius_meters=500.0,
            urgency=7.2,
            severity=7.5,
            vulnerability=3.6,
            accessibility_factor=0.80,
            estimated_stranded_count=26,
            water_level_m=1.05,
            power_status="OUT",
            status="TRIAGED",
        ),
        CriticalZone(
            id="ZONE-03",
            code="ZONE-CHARLIE",
            name="Metro Transit Underpass & Arterial",
            center_lat=13.0761,
            center_lon=80.2621,
            radius_meters=400.0,
            urgency=6.0,
            severity=5.5,
            vulnerability=2.2,
            accessibility_factor=0.75,
            estimated_stranded_count=16,
            water_level_m=0.9,
            power_status="NORMAL",
            status="TRIAGED",
        ),
        CriticalZone(
            id="ZONE-04",
            code="ZONE-ECHO",
            name="Riverside Relief Shelter Camp",
            center_lat=13.0701,
            center_lon=80.2551,
            radius_meters=350.0,
            urgency=4.0,
            severity=3.5,
            vulnerability=2.5,
            accessibility_factor=0.95,
            estimated_stranded_count=35,
            water_level_m=0.15,
            power_status="ON_BACKUP",
            status="TRIAGED",
        ),
    ]


def get_seed_resources() -> List[EmergencyResource]:
    """Returns operational fleet inventory available to the EOC."""
    return [
        EmergencyResource(
            id="RES-01",
            code="NDRF-BOAT-01",
            name="NDRF Heavy Flood Rescue Craft 01",
            type=ResourceType.NDRF_RESCUE_BOAT,
            capabilities=["FLOOD_EVAC", "DEEP_WATER", "AMPHIBIOUS"],
            base_station="Sector 2 Marine Depot",
            current_lat=13.0805,
            current_lon=80.2640,
            capacity_persons=12,
            speed_kmh=28.0,
            status=ResourceStatus.AVAILABLE,
            is_amphibious_or_air=True,
        ),
        EmergencyResource(
            id="RES-02",
            code="NDRF-BOAT-02",
            name="NDRF Rapid Inflatable Craft 02",
            type=ResourceType.NDRF_RESCUE_BOAT,
            capabilities=["FLOOD_EVAC", "DEEP_WATER", "AMPHIBIOUS"],
            base_station="North Pier Staging Station",
            current_lat=13.0890,
            current_lon=80.2790,
            capacity_persons=8,
            speed_kmh=32.0,
            status=ResourceStatus.AVAILABLE,
            is_amphibious_or_air=True,
        ),
        EmergencyResource(
            id="RES-03",
            code="SDRF-AMPH-01",
            name="SDRF Amphibious Rescue ATV 01",
            type=ResourceType.AMPHIBIOUS_ATV,
            capabilities=["FLOOD_EVAC", "AMPHIBIOUS", "DEEP_WATER"],
            base_station="Central Fire Headquarters",
            current_lat=13.0850,
            current_lon=80.2740,
            capacity_persons=6,
            speed_kmh=35.0,
            status=ResourceStatus.AVAILABLE,
            is_amphibious_or_air=True,
        ),
        EmergencyResource(
            id="RES-04",
            code="ALS-AMB-01",
            name="ALS Trauma Life Support Ambulance 01",
            type=ResourceType.ALS_AMBULANCE,
            capabilities=["TRAUMA_CARE", "ALS_AMBULANCE"],
            base_station="Metropolitan Health Depot",
            current_lat=13.0780,
            current_lon=80.2680,
            capacity_persons=2,
            speed_kmh=50.0,
            status=ResourceStatus.AVAILABLE,
            is_amphibious_or_air=False,
        ),
        EmergencyResource(
            id="RES-05",
            code="ALS-AMB-02",
            name="ALS Trauma Life Support Ambulance 02",
            type=ResourceType.ALS_AMBULANCE,
            capabilities=["TRAUMA_CARE", "ALS_AMBULANCE"],
            base_station="South Zone Dispensary",
            current_lat=13.0690,
            current_lon=80.2580,
            capacity_persons=2,
            speed_kmh=50.0,
            status=ResourceStatus.AVAILABLE,
            is_amphibious_or_air=False,
        ),
        EmergencyResource(
            id="RES-06",
            code="MED-EVAC-01",
            name="Quick Medical Evac Squad 01",
            type=ResourceType.MEDICAL_EVAC_TEAM,
            capabilities=["TRAUMA_CARE", "TRIAGE_MED"],
            base_station="Red Cross Regional Hub",
            current_lat=13.0720,
            current_lon=80.2590,
            capacity_persons=4,
            speed_kmh=45.0,
            status=ResourceStatus.AVAILABLE,
            is_amphibious_or_air=False,
        ),
        EmergencyResource(
            id="RES-07",
            code="HEAVY-PUMP-01",
            name="High-Capacity De-Watering & Gen Unit 01",
            type=ResourceType.HEAVY_PUMP_SUPPLY,
            capabilities=["POWER_SUPPORT", "DEWATERING"],
            base_station="Municipal Works Yard",
            current_lat=13.0810,
            current_lon=80.2660,
            capacity_persons=2,
            speed_kmh=30.0,
            status=ResourceStatus.AVAILABLE,
            is_amphibious_or_air=False,
        ),
        EmergencyResource(
            id="RES-08",
            code="DRONE-SKY-01",
            name="Thermal Recon Drone Squad 01",
            type=ResourceType.DRONE_RECON,
            capabilities=["SURVEILLANCE", "THERMAL_SCAN"],
            base_station="EOC Rooftop Station",
            current_lat=13.0830,
            current_lon=80.2720,
            capacity_persons=0,
            speed_kmh=75.0,
            status=ResourceStatus.AVAILABLE,
            is_amphibious_or_air=True,
        ),
    ]


def get_shock_event_data() -> Dict[str, Any]:
    """
    Returns Act II shock event:
    1. Bhatia Main Access Bridge Collapses (cuts off conventional road access).
    2. Flash surge & Toxic Hazmat breach at Industrial Chemical Corridor Ward 9.
    """
    return {
        "event_title": "Bhatia Bridge Collapse & Industrial Chemical Flash Breach",
        "description": "Bhatia Access Bridge collapsed, cutting primary arterial. Flash flood breach at Industrial Ward 9 trapped 52 workers near hazardous chemical storage with water surging past 1.7m.",
        "shock_zone": CriticalZone(
            id="ZONE-05",
            code="ZONE-DELTA",
            name="Industrial Chemical Corridor Ward 9",
            center_lat=13.0865,
            center_lon=80.2775,
            radius_meters=650.0,
            urgency=10.0,
            severity=9.8,
            vulnerability=4.9,  # Chemical hazard + high victim count
            accessibility_factor=0.50,  # Road collapsed / impassable
            estimated_stranded_count=52,
            water_level_m=1.75,
            power_status="OUT",
            status="TRIAGED",
        ),
        "bridge_collapse_point": {
            "name": "Bhatia Flyover & River Bridge",
            "lat": 13.0845,
            "lon": 80.2735,
            "status": "COLLAPSED",
            "affected_routes": ["Arterial Road 1", "Bridge Cross-Link"],
        },
    }
