import sys
import os
from datetime import datetime

# Add app parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from app.models.incident import RawEvidence, SourceType, RoadStatus
from app.models.zone import CriticalZone, TriageLevel
from app.models.resource import EmergencyResource, ResourceType, ResourceStatus
from app.engines.multi_source import MultiSourceEngine
from app.engines.critical_zone import CriticalZoneEngine
from app.engines.resource_allocator import ResourceAllocatorEngine
from app.engines.replanning import DynamicReplanningEngine


def test_engine_1_multi_source():
    print("\n--- TEST: Engine 1 (Multi-Source Intelligence) ---")
    engine = MultiSourceEngine(cluster_radius_m=350.0)

    # 4 reports in the same geographical area (~150m apart)
    reports = [
        RawEvidence(
            id="rep-01",
            source=SourceType.CITIZEN_SOS,
            latitude=13.0827,
            longitude=80.2707,
            description="Water rising fast near Central Market! 15 people trapped on terrace.",
            reported_casualties=15,
            road_status=RoadStatus.WATERLOGGED,
            water_depth_m=1.2,
            hazard_type="FLOOD",
        ),
        RawEvidence(
            id="rep-02",
            source=SourceType.IOT_SENSOR,
            latitude=13.0830,
            longitude=80.2710,
            description="Ultrasonic Sensor #W-104: Water level threshold breached.",
            reported_casualties=0,
            road_status=RoadStatus.SUBMERGED,
            water_depth_m=1.4,
            hazard_type="FLOOD",
        ),
        RawEvidence(
            id="rep-03",
            source=SourceType.CITIZEN_SOS,
            latitude=13.0828,
            longitude=80.2709,
            description="Motorbike just passed through, road seems clear from south end.",
            reported_casualties=2,
            road_status=RoadStatus.PASSABLE,
            water_depth_m=0.2,
            hazard_type="FLOOD",
        ),
        # 1 report in a distinct sector (2 km away)
        RawEvidence(
            id="rep-04",
            source=SourceType.EOC_DISPATCH,
            latitude=13.1000,
            longitude=80.2850,
            description="Substation feeder tripped near Industrial Park.",
            reported_casualties=0,
            road_status=RoadStatus.PASSABLE,
            water_depth_m=0.1,
            hazard_type="FLOOD",
        ),
    ]

    incidents = engine.process_evidence(reports)
    print(f"Aggregated {len(reports)} raw reports into {len(incidents)} clean incidents.")
    assert len(incidents) == 2, f"Expected 2 incidents, got {len(incidents)}"

    market_inc = incidents[0]
    print(f"Cluster 1 Title: {market_inc.title}")
    print(f"Verified Casualties: {market_inc.aggregated_casualties} ({market_inc.casualty_range})")
    print(f"Verified Road Status: {market_inc.verified_road_status}")
    print(f"Verified Water Depth: {market_inc.verified_water_depth_m}m")
    print(f"Evidence Confidence Score: {market_inc.confidence.score} ({market_inc.confidence.rationale})")
    print(f"Conflicts Detected: {len(market_inc.conflicts)}")

    for c in market_inc.conflicts:
        print(f"  -> Conflict [{c.conflict_type.value}]: {c.description}")

    # Assertions
    assert len(market_inc.conflicts) >= 1, "Should detect road status or water depth contradiction"
    assert market_inc.verified_road_status in [RoadStatus.SUBMERGED, RoadStatus.WATERLOGGED], "Should apply conservative safety rule"
    assert 0.1 <= market_inc.confidence.score <= 1.0
    print("[PASS] Engine 1 verification passed successfully!")


def test_engine_2_critical_zone():
    print("\n--- TEST: Engine 2 (Critical-Zone Intelligence) ---")
    engine = CriticalZoneEngine()

    # Zone Alpha: Severe Hospital ICU Crisis
    zone_hospital = CriticalZone(
        id="zone-01",
        name="District Hospital Sector 4",
        code="ZONE-ALPHA",
        center_lat=13.0827,
        center_lon=80.2707,
        urgency=9.5,
        severity=9.0,
        vulnerability=4.8,  # ICU Patients
        accessibility_factor=0.60,  # Flooded approach
        estimated_stranded_count=42,
        water_level_m=1.3,
        power_status="FAILING",
    )

    evaluated = engine.evaluate_priority(zone_hospital, evidence_confidence=0.92)
    print(f"Zone: {evaluated.name} ({evaluated.code})")
    print(f"Calculated Priority Score: {evaluated.priority_score} / 100")
    print(f"Triage Level: {evaluated.triage_level.value}")
    print(f"Breakdown Formula: {evaluated.score_breakdown.calculated_formula}")
    print(f"Required Capabilities: {evaluated.required_capabilities}")

    assert evaluated.triage_level == TriageLevel.CRITICAL_P1, "Hospital ICU should rank CRITICAL_P1"
    assert evaluated.priority_score >= 80.0
    assert "DEEP_WATER" in evaluated.required_capabilities
    assert "TRAUMA_CARE" in evaluated.required_capabilities
    print("[PASS] Engine 2 verification passed successfully!")


def test_engine_3_and_4_allocation_and_replanning():
    print("\n--- TEST: Engines 3 & 4 (Allocation & Dynamic Replanning) ---")
    allocator = ResourceAllocatorEngine()
    replanner = DynamicReplanningEngine()
    zone_engine = CriticalZoneEngine()

    # Three operational sectors
    zones = [
        zone_engine.evaluate_priority(
            CriticalZone(
                id="z-hospital",
                name="Metro General Hospital",
                code="ZONE-ALPHA",
                center_lat=13.0827,
                center_lon=80.2707,
                urgency=8.5,
                severity=9.0,
                vulnerability=4.5,
                accessibility_factor=0.65,
                estimated_stranded_count=35,
                water_level_m=1.2,
            )
        ),
        zone_engine.evaluate_priority(
            CriticalZone(
                id="z-market",
                name="Central Commercial Market",
                code="ZONE-BRAVO",
                center_lat=13.0900,
                center_lon=80.2800,
                urgency=5.0,
                severity=6.0,
                vulnerability=2.5,
                accessibility_factor=0.90,
                estimated_stranded_count=18,
                water_level_m=0.8,
            )
        ),
        zone_engine.evaluate_priority(
            CriticalZone(
                id="z-substation",
                name="Electrical Substation Ward 5",
                code="ZONE-CHARLIE",
                center_lat=13.0750,
                center_lon=80.2600,
                urgency=4.0,
                severity=4.0,
                vulnerability=2.0,
                accessibility_factor=0.95,
                estimated_stranded_count=8,
                water_level_m=0.2,
            )
        ),
    ]

    resources = [
        EmergencyResource(
            id="res-boat-01",
            code="NDRF-BOAT-01",
            name="NDRF Heavy Flood Rescue Boat",
            type=ResourceType.NDRF_RESCUE_BOAT,
            capabilities=["FLOOD_EVAC", "DEEP_WATER", "AMPHIBIOUS"],
            base_station="Sector 2 Marine Base",
            current_lat=13.0800,
            current_lon=80.2650,
            capacity_persons=12,
            speed_kmh=25.0,
            status=ResourceStatus.AVAILABLE,
            is_amphibious_or_air=True,
        ),
        EmergencyResource(
            id="res-boat-02",
            code="NDRF-BOAT-02",
            name="NDRF Rapid Inflatable Craft",
            type=ResourceType.NDRF_RESCUE_BOAT,
            capabilities=["FLOOD_EVAC", "DEEP_WATER", "AMPHIBIOUS"],
            base_station="North Pier Staging Area",
            current_lat=13.0880,
            current_lon=80.2780,
            capacity_persons=8,
            speed_kmh=30.0,
            status=ResourceStatus.AVAILABLE,
            is_amphibious_or_air=True,
        ),
        EmergencyResource(
            id="res-amb-01",
            code="ALS-AMB-01",
            name="ALS Trauma Ambulance",
            type=ResourceType.ALS_AMBULANCE,
            capabilities=["TRAUMA_CARE", "ALS_AMBULANCE"],
            base_station="Civil Hospital Depot",
            current_lat=13.0760,
            current_lon=80.2610,
            capacity_persons=2,
            speed_kmh=45.0,
            status=ResourceStatus.AVAILABLE,
            is_amphibious_or_air=False,
        ),
    ]

    # Initial Plan Generation (Act I)
    initial_plan = allocator.generate_plan(zones=zones, resources=resources, plan_version=1)
    print(f"\nInitial Plan ID: {initial_plan.id} (Version {initial_plan.plan_version})")
    print(f"Strategic Summary: {initial_plan.strategic_summary}")
    assert len(initial_plan.decisions) == 3, f"Expected 3 allocations, got {len(initial_plan.decisions)}"

    for dec in initial_plan.decisions:
        print(f"  Assignment: {dec.resource_code} -> {dec.target_zone_name} (ETA: {dec.eta_minutes} min)")
        print(f"    Reasoning: {dec.explanation_why_this_unit}")
        print(f"    Alternative: {dec.alternative_rejected}")

    # Shock Event: Sudden Flash Inundation & Gas Leak at Industrial Corridor (Act II)
    print("\n--- INJECTING EVENT: Flash Breach & Toxic Runoff at Industrial Corridor ---")
    hazmat_zone = zone_engine.evaluate_priority(
        CriticalZone(
            id="z-hazmat",
            name="Industrial Corridor Ward 9",
            code="ZONE-DELTA",
            center_lat=13.0870,
            center_lon=80.2760,
            urgency=10.0,
            severity=9.8,
            vulnerability=4.9,
            accessibility_factor=0.55,
            estimated_stranded_count=45,
            water_level_m=1.6,
        )
    )

    # Update zones list: Add urgent P1 hazmat zone, degrade access
    updated_zones = [zones[0], hazmat_zone, zones[1], zones[2]]

    new_plan, diff = replanner.process_replan(
        current_plan=initial_plan,
        trigger_event_title="Industrial Flash Breach & Toxic Runoff",
        trigger_event_description="Flood barrier collapsed at Industrial Ward 9; 45 workers stranded with rising toxic floodwaters.",
        updated_zones=updated_zones,
        all_resources=resources,
    )

    print(f"\nReplan Generated: {new_plan.id} (v{new_plan.plan_version})")
    print(f"Diff Summary: {diff.executive_diff_summary}")
    print(f"Lives Risk Delta: {diff.lives_risk_delta_explanation}")
    print(f"Diverted Count: {diff.diverted_count}")

    for change in diff.changes:
        print(f"  Change [{change.change_type}]: Unit {change.resource_code} "
              f"({change.old_zone_name or 'Reserve'} -> {change.new_zone_name}) | Reason: {change.reason}")

    assert new_plan.plan_version == 2
    assert diff.old_plan_id == initial_plan.id
    assert diff.new_plan_id == new_plan.id
    assert diff.diverted_count >= 1, "Expected at least 1 unit diversion to the new P1 crisis"
    print("[PASS] Engines 3 & 4 verification passed successfully!")


if __name__ == "__main__":
    print("Running RESQ-AI Core Engines Test Suite...")
    test_engine_1_multi_source()
    test_engine_2_critical_zone()
    test_engine_3_and_4_allocation_and_replanning()
    print("\n=======================================================")
    print("ALL CORE ENGINES VALIDATED AND FUNCTIONING CORRECTLY!")
    print("=======================================================\n")
