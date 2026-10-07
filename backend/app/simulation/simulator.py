import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.incident import RawEvidence, Incident, Conflict
from ..models.zone import CriticalZone
from ..models.resource import EmergencyResource, ResourceStatus
from ..models.plan import ResourcePlan, PlanDiff, PlanStatus, DecisionStatus
from ..engines.multi_source import MultiSourceEngine
from ..engines.critical_zone import CriticalZoneEngine
from ..engines.resource_allocator import ResourceAllocatorEngine
from ..engines.replanning import DynamicReplanningEngine
from .scenario_data import (
    get_seed_raw_evidence,
    get_seed_zones,
    get_seed_resources,
    get_shock_event_data,
)


class DisasterSimulator:
    """
    Simulation State Controller for RESQ-AI.
    Manages deterministic 3-Act live disaster progression for Hackathon Demonstrations.
    """

    def __init__(self):
        self.multi_source_engine = MultiSourceEngine()
        self.zone_engine = CriticalZoneEngine()
        self.allocator_engine = ResourceAllocatorEngine()
        self.replanning_engine = DynamicReplanningEngine()
        self.reset()

    def reset(self):
        """Resets the simulation to fresh Act I state."""
        self.current_act = 1
        self.act_title = "Act I: Multi-Source Evidence Influx"
        self.act_description = "Fragmented citizen SOS calls, IoT flood gauges, and drone recon ingested and verified."
        self.raw_evidence: List[RawEvidence] = get_seed_raw_evidence()
        self.incidents: List[Incident] = self.multi_source_engine.process_evidence(self.raw_evidence)
        
        # Initialize zones with evaluated priorities
        base_zones = get_seed_zones()
        self.zones: List[CriticalZone] = [
            self.zone_engine.evaluate_priority(z) for z in base_zones
        ]
        self.resources: List[EmergencyResource] = get_seed_resources()
        
        # Initial allocation plan
        self.current_plan: ResourcePlan = self.allocator_engine.generate_plan(
            zones=self.zones,
            resources=self.resources,
            plan_version=1,
            is_replan=False,
        )
        self.plans_history: List[ResourcePlan] = [self.current_plan]
        self.latest_diff: Optional[PlanDiff] = None
        self.audit_log: List[Dict[str, Any]] = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "action": "SIMULATION_INITIATED",
                "actor": "SYSTEM",
                "details": "Act I started: 9 raw reports aggregated into 4 critical zones. Plan v1 formulated.",
            }
        ]

    def trigger_act_2_shock(self) -> Dict[str, Any]:
        """
        Triggers Act II: Bhatia Bridge Collapse + Chemical Corridor Flash Inundation.
        Forces the Dynamic Replanning Engine to execute and produce an Old vs New Plan diff.
        """
        self.current_act = 2
        self.act_title = "Act II: Critical Shock & Automated Replanning"
        self.act_description = "Bridge collapse isolates arterial route; flash surge strikes Chemical Corridor. Engine re-optimizes."

        shock = get_shock_event_data()
        shock_zone = self.zone_engine.evaluate_priority(shock["shock_zone"])

        # Also degrade accessibility to Hospital due to collapsed bridge
        for z in self.zones:
            if z.code == "ZONE-ALPHA":
                z.urgency = 10.0
                z.severity = 9.8
                z.water_level_m = 1.7
                z.accessibility_factor = 0.50  # Bridge approach collapsed!
                self.zone_engine.evaluate_priority(z)

        # Append new high-criticality zone if not already present
        if not any(z.id == shock_zone.id for z in self.zones):
            self.zones.append(shock_zone)

        # Re-sort and re-evaluate all zones
        self.zones = self.zone_engine.rank_zones([self.zone_engine.evaluate_priority(z) for z in self.zones])

        # Execute replan!
        new_plan, diff = self.replanning_engine.process_replan(
            current_plan=self.current_plan,
            trigger_event_title=shock["event_title"],
            trigger_event_description=shock["description"],
            updated_zones=self.zones,
            all_resources=self.resources,
        )

        self.current_plan = new_plan
        self.plans_history.append(new_plan)
        self.latest_diff = diff

        self.audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "DYNAMIC_REPLAN_TRIGGERED",
            "actor": "ENGINE_4_REPLANNER",
            "details": f"Shock event injected. Diverted {diff.diverted_count} units. Plan v{new_plan.plan_version} generated.",
        })

        return {
            "act": self.current_act,
            "title": self.act_title,
            "new_plan": self.current_plan,
            "diff": self.latest_diff,
        }

    def trigger_act_3_approval_and_dispatch(
        self, commander_name: str = "Commander V. Sharma", notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Triggers Act III: EOC Commander reviews and officially approves the plan.
        Dispatches all units and transitions operational state.
        """
        self.current_act = 3
        self.act_title = "Act III: Human Commander Authorization & Dispatch"
        self.act_description = f"Authorized by {commander_name}. Resources mobilized under active telemetry tracking."

        self.current_plan.status = PlanStatus.APPROVED
        for dec in self.current_plan.decisions:
            dec.status = DecisionStatus.APPROVED

        # Update resource statuses to reflect active deployment
        assigned_res_ids = {d.resource_id: d for d in self.current_plan.decisions}
        for res in self.resources:
            if res.id in assigned_res_ids:
                res.status = ResourceStatus.EN_ROUTE
                res.current_assigned_zone_id = assigned_res_ids[res.id].target_zone_id
                res.estimated_arrival_minutes = assigned_res_ids[res.id].eta_minutes

        self.audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "PLAN_OFFICIALLY_APPROVED",
            "actor": commander_name,
            "details": f"Plan v{self.current_plan.plan_version} approved. {len(self.current_plan.decisions)} units actively mobilized.",
            "notes": notes or "All safety trade-offs reviewed and sanctioned.",
        })

        return {
            "act": self.current_act,
            "title": self.act_title,
            "status": "APPROVED",
            "plan": self.current_plan,
        }

    def override_decision(
        self,
        decision_id: str,
        new_resource_id: str,
        commander_name: str,
        reason: str,
    ) -> Dict[str, Any]:
        """Allows human commander to manually override an allocation decision."""
        target_dec = None
        for d in self.current_plan.decisions:
            if d.id == decision_id:
                target_dec = d
                break

        if not target_dec:
            raise ValueError(f"Decision {decision_id} not found in current plan.")

        old_res_code = target_dec.resource_code
        new_res = next((r for r in self.resources if r.id == new_resource_id), None)
        if not new_res:
            raise ValueError(f"Resource {new_resource_id} not found.")

        target_dec.resource_id = new_res.id
        target_dec.resource_code = new_res.code
        target_dec.resource_type = new_res.type.value
        target_dec.status = DecisionStatus.OVERRIDDEN
        target_dec.commander_override_reason = reason
        target_dec.explanation_why_this_unit += f" [COMMANDER OVERRIDE by {commander_name}: {reason}]"

        self.audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "COMMANDER_DECISION_OVERRIDE",
            "actor": commander_name,
            "details": f"Decision {decision_id} modified: Replaced {old_res_code} with {new_res.code}. Reason: {reason}",
        })

        return {"status": "OVERRIDDEN", "decision": target_dec}

    def get_full_state(self) -> Dict[str, Any]:
        """Returns the complete synchronized state for the frontend EOC dashboard."""
        all_conflicts = []
        for inc in self.incidents:
            all_conflicts.extend(inc.conflicts)

        return {
            "current_act": self.current_act,
            "act_title": self.act_title,
            "act_description": self.act_description,
            "is_simulation": True,
            "simulation_disclaimer": "SIMULATION ENVIRONMENT // FOR TRAINING & DECISION SUPPORT DEMONSTRATION ONLY",
            "raw_evidence_count": len(self.raw_evidence),
            "incidents": self.incidents,
            "conflicts": all_conflicts,
            "zones": self.zones,
            "resources": self.resources,
            "current_plan": self.current_plan,
            "plans_history_count": len(self.plans_history),
            "latest_diff": self.latest_diff,
            "audit_log": self.audit_log,
        }


# Singleton simulator instance for the application
simulator = DisasterSimulator()
