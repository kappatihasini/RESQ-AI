import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ..models.plan import (
    ResourcePlan,
    PlanDiff,
    PlanDiffItem,
    AllocationDecision,
    PlanStatus,
    DecisionStatus,
)
from ..models.zone import CriticalZone, TriageLevel
from ..models.resource import EmergencyResource, ResourceStatus
from .resource_allocator import ResourceAllocatorEngine
from .critical_zone import CriticalZoneEngine


class DynamicReplanningEngine:
    """
    Engine 4: Dynamic Replanning Engine.
    Continuously monitors environmental delta events, triggers immediate re-optimization,
    and produces side-by-side 'Old Plan vs New Plan' diffs with trade-off explanations.
    """

    def __init__(self):
        self.allocator = ResourceAllocatorEngine()
        self.zone_engine = CriticalZoneEngine()

    def process_replan(
        self,
        current_plan: ResourcePlan,
        trigger_event_title: str,
        trigger_event_description: str,
        updated_zones: List[CriticalZone],
        all_resources: List[EmergencyResource],
    ) -> Tuple[ResourcePlan, PlanDiff]:
        """
        Executes dynamic re-optimization and generates the differential comparison.
        """
        new_version = current_plan.plan_version + 1

        # Re-evaluate all zones with updated conditions
        ranked_zones = [
            self.zone_engine.evaluate_priority(z) for z in updated_zones
        ]

        # Generate new optimized plan
        new_plan = self.allocator.generate_plan(
            zones=ranked_zones,
            resources=all_resources,
            plan_version=new_version,
            is_replan=True,
            trigger_event=f"{trigger_event_title}: {trigger_event_description}",
        )

        # Build Old Plan vs New Plan Differential
        old_decision_map: Dict[str, AllocationDecision] = {
            d.resource_id: d for d in current_plan.decisions
        }
        new_decision_map: Dict[str, AllocationDecision] = {
            d.resource_id: d for d in new_plan.decisions
        }

        diff_items: List[PlanDiffItem] = []
        diverted_count = 0
        newly_assigned_count = 0

        # Check all resources in the new plan
        for res_id, new_dec in new_decision_map.items():
            if res_id in old_decision_map:
                old_dec = old_decision_map[res_id]
                if old_dec.target_zone_id != new_dec.target_zone_id:
                    # Resource was DIVERTED!
                    diverted_count += 1
                    diff_items.append(
                        PlanDiffItem(
                            resource_id=res_id,
                            resource_code=new_dec.resource_code,
                            old_zone_id=old_dec.target_zone_id,
                            old_zone_name=old_dec.target_zone_name,
                            new_zone_id=new_dec.target_zone_id,
                            new_zone_name=new_dec.target_zone_name,
                            old_eta=old_dec.eta_minutes,
                            new_eta=new_dec.eta_minutes,
                            change_type="DIVERTED",
                            reason=(
                                f"Preempted from {old_dec.target_zone_name} ({old_dec.target_zone_triage}) "
                                f"to urgent sector {new_dec.target_zone_name} ({new_dec.target_zone_triage}) "
                                f"due to: {trigger_event_title}."
                            ),
                        )
                    )
                elif abs(new_dec.eta_minutes - old_dec.eta_minutes) > 2.0:
                    # Resource re-routed due to obstacle
                    diff_items.append(
                        PlanDiffItem(
                            resource_id=res_id,
                            resource_code=new_dec.resource_code,
                            old_zone_id=old_dec.target_zone_id,
                            old_zone_name=old_dec.target_zone_name,
                            new_zone_id=new_dec.target_zone_id,
                            new_zone_name=new_dec.target_zone_name,
                            old_eta=old_dec.eta_minutes,
                            new_eta=new_dec.eta_minutes,
                            change_type="RE-ROUTED",
                            reason=f"Detour required due to accessibility friction changes. ETA delta: +{round(new_dec.eta_minutes - old_dec.eta_minutes, 1)} min.",
                        )
                    )
            else:
                newly_assigned_count += 1
                diff_items.append(
                    PlanDiffItem(
                        resource_id=res_id,
                        resource_code=new_dec.resource_code,
                        old_zone_id=None,
                        old_zone_name=None,
                        new_zone_id=new_dec.target_zone_id,
                        new_zone_name=new_dec.target_zone_name,
                        old_eta=None,
                        new_eta=new_dec.eta_minutes,
                        change_type="NEWLY_ASSIGNED",
                        reason=f"Mobilized from staging reserve to support {new_dec.target_zone_name}.",
                    )
                )

        # Check resources released or cancelled
        for res_id, old_dec in old_decision_map.items():
            if res_id not in new_decision_map:
                diff_items.append(
                    PlanDiffItem(
                        resource_id=res_id,
                        resource_code=old_dec.resource_code,
                        old_zone_id=old_dec.target_zone_id,
                        old_zone_name=old_dec.target_zone_name,
                        new_zone_id=None,
                        new_zone_name=None,
                        old_eta=old_dec.eta_minutes,
                        new_eta=None,
                        change_type="RELEASED",
                        reason="Reassigned to reserve standby.",
                    )
                )

        lives_delta_text = (
            f"Replanning response ensures critical coverage for {trigger_event_title}. "
            f"Redirected {diverted_count} units directly mitigating immediate mortality risk "
            f"while maintaining minimum threshold stability across secondary sectors."
        )

        executive_summary = (
            f"Dynamic Replan triggered by '{trigger_event_title}'. "
            f"{diverted_count} critical diversions, {newly_assigned_count} reserve activations. "
            f"New Plan v{new_version} generated with average ETA {new_plan.total_avg_eta_minutes} min."
        )

        diff = PlanDiff(
            id=f"DIFF-{uuid.uuid4().hex[:6]}",
            timestamp=datetime.utcnow(),
            old_plan_id=current_plan.id,
            new_plan_id=new_plan.id,
            trigger_event_title=trigger_event_title,
            trigger_event_description=trigger_event_description,
            changes=diff_items,
            diverted_count=diverted_count,
            newly_assigned_count=newly_assigned_count,
            lives_risk_delta_explanation=lives_delta_text,
            executive_diff_summary=executive_summary,
        )

        return new_plan, diff
