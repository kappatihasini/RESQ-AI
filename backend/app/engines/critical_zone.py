import math
from typing import List, Dict, Any, Optional

from ..models.zone import CriticalZone, TriageLevel, ScoreBreakdown
from ..models.incident import Incident, RoadStatus


class CriticalZoneEngine:
    """
    Engine 2: Critical-Zone Intelligence Engine.
    Evaluates geographical zones, calculates explainable priority scores,
    and assigns triage levels based on multidimensional risk factors.
    """

    # Transparent weights
    WEIGHT_URGENCY = 4.0      # Urgency (1.0 to 10.0) -> Max 40
    WEIGHT_SEVERITY = 4.0     # Severity (1.0 to 10.0) -> Max 40
    WEIGHT_VULNERABILITY = 4.0 # Vulnerability (1.0 to 5.0) -> Max 20

    ROAD_ACCESSIBILITY_MAP = {
        RoadStatus.PASSABLE: 1.00,
        RoadStatus.SLOW_TRAFFIC: 0.95,
        RoadStatus.WATERLOGGED: 0.85,
        RoadStatus.BLOCKED: 0.70,
        RoadStatus.SUBMERGED: 0.60,
        RoadStatus.COLLAPSED: 0.50,
    }

    def evaluate_priority(
        self,
        zone: CriticalZone,
        evidence_confidence: float = 0.90,
    ) -> CriticalZone:
        """
        Calculates mathematical priority score with full explainability breakdown.
        """
        # Clamp inputs
        urg = max(1.0, min(10.0, zone.urgency))
        sev = max(1.0, min(10.0, zone.severity))
        vul = max(1.0, min(5.0, zone.vulnerability))
        acc = max(0.5, min(1.0, zone.accessibility_factor))
        conf = max(0.2, min(1.0, evidence_confidence))

        # 1. Base component calculations
        u_weighted = urg * self.WEIGHT_URGENCY           # [4.0 .. 40.0]
        s_weighted = sev * self.WEIGHT_SEVERITY          # [4.0 .. 40.0]
        v_weighted = vul * self.WEIGHT_VULNERABILITY     # [4.0 .. 20.0]
        base_score = u_weighted + s_weighted + v_weighted # [12.0 .. 100.0]

        # 2. Accessibility friction adjustment:
        # Lower accessibility (e.g., flooded/collapsed roads) compounds danger and requires specialized priority
        isolation_friction = 1.0 + ((1.0 - acc) * 0.40)  # [1.0 .. 1.20]

        # 3. Evidence confidence multiplier:
        # High confidence confirms priority; unverified noise is discounted
        raw_final = (base_score * isolation_friction) * conf
        final_score = round(max(5.0, min(100.0, raw_final)), 1)

        # 4. Triage Classification
        if final_score >= 80.0:
            triage = TriageLevel.CRITICAL_P1
        elif final_score >= 60.0:
            triage = TriageLevel.HIGH_P2
        elif final_score >= 40.0:
            triage = TriageLevel.MEDIUM_P3
        else:
            triage = TriageLevel.LOW_P4

        # 5. Explainable breakdown
        formula_str = (
            f"({self.WEIGHT_URGENCY}×{urg} + {self.WEIGHT_SEVERITY}×{sev} + {self.WEIGHT_VULNERABILITY}×{vul}) "
            f"× (1 + (1 - {acc:.2f})×0.4) × {conf:.2f} = {final_score}"
        )

        rationale = (
            f"Triage {triage.value} assigned. Urgency contributes {u_weighted:.1f} pts, "
            f"Severity contributes {s_weighted:.1f} pts, Vulnerability contributes {v_weighted:.1f} pts. "
            f"Access friction factor: x{isolation_friction:.2f}. Verified confidence: x{conf:.2f}."
        )

        breakdown = ScoreBreakdown(
            urgency_raw=round(urg, 1),
            urgency_weighted=round(u_weighted, 1),
            severity_raw=round(sev, 1),
            severity_weighted=round(s_weighted, 1),
            vulnerability_raw=round(vul, 1),
            vulnerability_weighted=round(v_weighted, 1),
            accessibility_factor=round(acc, 2),
            evidence_confidence=round(conf, 2),
            calculated_formula=formula_str,
            explanation=rationale,
        )

        # Derive required capabilities dynamically
        req_caps = set(zone.required_capabilities)
        if zone.water_level_m >= 1.0:
            req_caps.update(["DEEP_WATER", "FLOOD_EVAC", "AMPHIBIOUS"])
        elif zone.water_level_m >= 0.4:
            req_caps.update(["FLOOD_EVAC"])

        if zone.power_status in ["FAILING", "OUT"] or "HOSPITAL" in zone.name.upper() or "ICU" in zone.name.upper():
            req_caps.update(["TRAUMA_CARE", "ALS_AMBULANCE", "POWER_SUPPORT"])

        if acc <= 0.70:
            req_caps.add("AMPHIBIOUS")

        zone.priority_score = final_score
        zone.triage_level = triage
        zone.score_breakdown = breakdown
        zone.required_capabilities = sorted(list(req_caps))

        return zone

    def rank_zones(self, zones: List[CriticalZone]) -> List[CriticalZone]:
        """Ranks zones in descending order of calculated priority score."""
        return sorted(zones, key=lambda z: z.priority_score, reverse=True)
