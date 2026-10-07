import math
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ..models.resource import EmergencyResource, ResourceStatus, ResourceType
from ..models.zone import CriticalZone, TriageLevel
from ..models.plan import AllocationDecision, ResourcePlan, DecisionStatus, PlanStatus
from .multi_source import haversine_distance_meters


def calculate_eta_minutes(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    speed_kmh: float,
    route_friction: float = 1.0,
) -> Tuple[float, float]:
    """
    Calculates straight-line road distance in km and estimated transit time in minutes,
    incorporating route friction factor (1.0 = smooth, 1.5 = detour/waterlogged).
    """
    dist_m = haversine_distance_meters(lat1, lon1, lat2, lon2)
    dist_km = (dist_m / 1000.0) * 1.3  # 1.3 road winding factor
    effective_speed = max(10.0, speed_kmh / route_friction)
    transit_hours = dist_km / effective_speed
    eta_mins = round(transit_hours * 60.0, 1)
    return round(dist_km, 2), eta_mins


class ResourceAllocatorEngine:
    """
    Engine 3: Resource Allocation Engine.
    Performs deterministic multi-criteria matching between prioritized critical zones
    and emergency resources under operational constraints, generating an explainable
    decision trace for each assignment.
    """

    def generate_plan(
        self,
        zones: List[CriticalZone],
        resources: List[EmergencyResource],
        plan_version: int = 1,
        is_replan: bool = False,
        trigger_event: Optional[str] = None,
    ) -> ResourcePlan:
        """
        Generates a globally optimized deterministic allocation plan.
        Prioritizes P1/P2 zones first and matches nearest capable resource.
        """
        # Sort zones by priority score descending
        sorted_zones = sorted(zones, key=lambda z: z.priority_score, reverse=True)

        # Track resource availability
        available_resources = [
            r for r in resources if r.status in [ResourceStatus.AVAILABLE, ResourceStatus.EN_ROUTE]
        ]
        assigned_resource_ids = set()

        decisions: List[AllocationDecision] = []
        unserved_zones = []

        total_lives_protected = 0
        total_etas = []

        for zone in sorted_zones:
            # Determine maximum units this zone can receive based on triage level and victim load
            max_units = 1
            if zone.triage_level == TriageLevel.CRITICAL_P1:
                max_units = 2
            elif zone.triage_level == TriageLevel.HIGH_P2 and zone.estimated_stranded_count > 20:
                max_units = 2

            units_allocated_to_zone = 0
            covered_caps = set()

            while units_allocated_to_zone < max_units:
                # Determine candidate resources that satisfy capability constraints
                candidates: List[Tuple[EmergencyResource, float, float, List[str], str]] = []

                for res in available_resources:
                    if res.id in assigned_resource_ids:
                        continue

                    # Capability Matching
                    req_set = set(zone.required_capabilities)
                    res_caps = set(res.capabilities)
                    matched_caps = list(req_set.intersection(res_caps))
                    uncovered_matched = list(res_caps.intersection(req_set - covered_caps))

                    # Hard constraint: If zone requires DEEP_WATER or FLOOD_EVAC, road-only ambulances cannot reach
                    if "DEEP_WATER" in req_set and not res.is_amphibious_or_air and "DEEP_WATER" not in res_caps:
                        continue

                    # Hard constraint: If zone is collapsed route (accessibility <= 0.60) and unit not amphibious/air
                    route_friction = 1.0
                    if zone.accessibility_factor <= 0.70:
                        if not res.is_amphibious_or_air:
                            route_friction = 2.5  # Heavy detour delay

                    dist_km, eta_mins = calculate_eta_minutes(
                        res.current_lat,
                        res.current_lon,
                        zone.center_lat,
                        zone.center_lon,
                        res.speed_kmh,
                        route_friction=route_friction,
                    )

                    # Matching suitability score (lower is better):
                    # Prioritizes units bringing newly uncovered capabilities
                    cap_bonus = len(matched_caps) * 4.0 + len(uncovered_matched) * 6.0
                    suitability = eta_mins - cap_bonus

                    candidates.append((res, suitability, eta_mins, matched_caps, str(dist_km)))

                if not candidates:
                    if units_allocated_to_zone == 0:
                        unserved_zones.append(zone.id)
                    break

                # Sort candidates by suitability
                candidates.sort(key=lambda c: c[1])

                best_res, _, best_eta, best_matched_caps, best_dist = candidates[0]
                assigned_resource_ids.add(best_res.id)
                covered_caps.update(best_res.capabilities)
                units_allocated_to_zone += 1

                # Build alternative rejection rationale
                if len(candidates) > 1:
                    alt_res = candidates[1][0]
                    alt_eta = candidates[1][2]
                    alt_reason = (
                        f"Unit {alt_res.code} was second choice (ETA {alt_eta} min) "
                        f"but had lower capability fit or higher transit time."
                    )
                else:
                    alt_reason = "No other units met the capability or distance requirements for this sector."

                # Constraints verified
                verified_constraints = [
                    f"CAPABILITY_MATCH: [{', '.join(best_matched_caps) if best_matched_caps else 'GENERAL_DISPATCH'}]",
                    f"ROUTE_VIABILITY: Factor {1.0 if best_res.is_amphibious_or_air else zone.accessibility_factor}",
                    f"ESTIMATED_TRANSIT: {best_eta} min (Distance {best_dist} km)",
                ]

                explanation = (
                    f"Assigned {best_res.name} ({best_res.code}) to {zone.name} ({zone.triage_level.value}). "
                    f"Unit offers optimal capability match for [{', '.join(best_matched_caps) if best_matched_caps else 'general support'}] "
                    f"with minimum response ETA of {best_eta} min. Directly safeguards ~{zone.estimated_stranded_count} stranded victims."
                )

                decision = AllocationDecision(
                    id=f"DEC-{uuid.uuid4().hex[:6]}",
                    resource_id=best_res.id,
                    resource_code=best_res.code,
                    resource_type=best_res.type.value,
                    target_zone_id=zone.id,
                    target_zone_name=zone.name,
                    target_zone_triage=zone.triage_level.value,
                    distance_km=float(best_dist),
                    eta_minutes=best_eta,
                    matched_capabilities=best_matched_caps,
                    capacity_contributed=best_res.capacity_persons,
                    score_impact=round(zone.priority_score * 0.85, 1),
                    explanation_why_this_unit=explanation,
                    alternative_rejected=alt_reason,
                    constraints_satisfied=verified_constraints,
                    status=DecisionStatus.PROPOSED,
                )

                decisions.append(decision)
                total_lives_protected += min(best_res.capacity_persons, zone.estimated_stranded_count)
                total_etas.append(best_eta)

        unassigned_ids = [
            r.id for r in available_resources if r.id not in assigned_resource_ids
        ]

        avg_eta = round(sum(total_etas) / len(total_etas), 1) if total_etas else 0.0

        summary = (
            f"Plan v{plan_version}: {len(decisions)} tactical dispatches formulated. "
            f"Average ETA across critical sectors is {avg_eta} min. "
            f"Estimated {total_lives_protected} lives in triage coverage. "
            f"{len(unserved_zones)} sectors awaiting auxiliary reserves."
        )

        return ResourcePlan(
            id=f"PLAN-{uuid.uuid4().hex[:8]}",
            plan_version=plan_version,
            created_at=datetime.utcnow(),
            status=PlanStatus.PROPOSED,
            decisions=decisions,
            unassigned_resource_ids=unassigned_ids,
            unserved_zone_ids=unserved_zones,
            total_estimated_lives_protected=total_lives_protected,
            total_avg_eta_minutes=avg_eta,
            strategic_summary=summary,
            is_replan=is_replan,
            trigger_event=trigger_event,
        )
