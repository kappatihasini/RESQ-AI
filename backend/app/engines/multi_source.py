import math
import uuid
from typing import List, Dict, Any, Tuple
from datetime import datetime

from ..models.incident import (
    RawEvidence,
    Incident,
    Conflict,
    ConflictType,
    EvidenceConfidence,
    RoadStatus,
    SourceType,
)


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two coordinates in meters."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class MultiSourceEngine:
    """
    Engine 1: Multi-Source Intelligence Engine.
    Converts noisy, fragmented, multi-source emergency reports into verified,
    deduplicated, conflict-aware incident records with explainable confidence.
    """

    SPATIAL_CLUSTER_RADIUS_M = 350.0  # Cluster radius
    SOURCE_WEIGHTS = {
        SourceType.IOT_SENSOR: 0.95,
        SourceType.EOC_DISPATCH: 0.92,
        SourceType.FIELD_DRONE: 0.88,
        SourceType.CITIZEN_SOS: 0.70,
    }

    def __init__(self, cluster_radius_m: float = 350.0):
        self.cluster_radius_m = cluster_radius_m

    def cluster_evidence(self, raw_reports: List[RawEvidence]) -> List[List[RawEvidence]]:
        """
        Clusters raw reports using spatial proximity and hazard similarity.
        Deterministic spatial greedy clustering.
        """
        if not raw_reports:
            return []

        clusters: List[List[RawEvidence]] = []
        assigned = set()

        for i, rep_a in enumerate(raw_reports):
            if i in assigned:
                continue

            current_cluster = [rep_a]
            assigned.add(i)

            for j, rep_b in enumerate(raw_reports):
                if j in assigned:
                    continue

                dist = haversine_distance_meters(
                    rep_a.latitude, rep_a.longitude, rep_b.latitude, rep_b.longitude
                )

                same_hazard = rep_a.hazard_type.upper() == rep_b.hazard_type.upper()
                if dist <= self.cluster_radius_m and same_hazard:
                    current_cluster.append(rep_b)
                    assigned.add(j)

            clusters.append(current_cluster)

        return clusters

    def detect_conflicts(self, cluster: List[RawEvidence]) -> List[Conflict]:
        """
        Detects operational contradictions and discrepancies across multi-source reports.
        """
        conflicts: List[Conflict] = []
        if len(cluster) < 2:
            return conflicts

        evidence_ids = [e.id for e in cluster]

        # 1. Road Status Contradiction
        clear_statuses = {RoadStatus.PASSABLE, RoadStatus.SLOW_TRAFFIC}
        blocked_statuses = {RoadStatus.BLOCKED, RoadStatus.SUBMERGED, RoadStatus.COLLAPSED}

        has_clear = any(e.road_status in clear_statuses for e in cluster)
        has_blocked = any(e.road_status in blocked_statuses for e in cluster)

        if has_clear and has_blocked:
            clear_sources = [f"{e.source.value} ({e.road_status.value})" for e in cluster if e.road_status in clear_statuses]
            blocked_sources = [f"{e.source.value} ({e.road_status.value})" for e in cluster if e.road_status in blocked_statuses]
            conflicts.append(
                Conflict(
                    id=f"cnf-{uuid.uuid4().hex[:6]}",
                    conflict_type=ConflictType.ROAD_STATUS_CONTRADICTION,
                    evidence_ids=evidence_ids,
                    severity="CRITICAL",
                    description=(
                        f"Road accessibility contradiction: [{', '.join(clear_sources)}] vs "
                        f"[{', '.join(blocked_sources)}]. Conservative triage applied (assumed impassable)."
                    ),
                    resolution_status="FLAGGED",
                    resolution_note="Requires drone or field scout verification; conservative routing enforced.",
                )
            )

        # 2. Casualty Count Discrepancy
        casualties = [e.reported_casualties for e in cluster if e.reported_casualties > 0]
        if len(casualties) >= 2:
            min_c = min(casualties)
            max_c = max(casualties)
            if max_c >= 3 * min_c and (max_c - min_c) >= 5:
                conflicts.append(
                    Conflict(
                        id=f"cnf-{uuid.uuid4().hex[:6]}",
                        conflict_type=ConflictType.CASUALTY_DISCREPANCY,
                        evidence_ids=evidence_ids,
                        severity="MEDIUM",
                        description=(
                            f"Significant divergence in reported casualty figures: min {min_c} vs max {max_c} victims. "
                            f"Upper-bound preparedness buffer allocated."
                        ),
                        resolution_status="FLAGGED",
                    )
                )

        # 3. Water Depth Mismatch (> 1.0m difference)
        depths = [e.water_depth_m for e in cluster if e.water_depth_m > 0]
        if len(depths) >= 2:
            min_d = min(depths)
            max_d = max(depths)
            if (max_d - min_d) >= 1.0:
                conflicts.append(
                    Conflict(
                        id=f"cnf-{uuid.uuid4().hex[:6]}",
                        conflict_type=ConflictType.WATER_DEPTH_MISMATCH,
                        evidence_ids=evidence_ids,
                        severity="HIGH",
                        description=(
                            f"Discrepancy in recorded water levels: {min_d:.1f}m vs {max_d:.1f}m. "
                            f"Boat deployment prioritized."
                        ),
                        resolution_status="FLAGGED",
                    )
                )

        return conflicts

    def calculate_confidence(
        self, cluster: List[RawEvidence], conflicts: List[Conflict]
    ) -> EvidenceConfidence:
        """
        Calculates mathematical evidence confidence score C_ev in [0.0, 1.0].
        Considers source credibility, cross-validation count, freshness, and conflict penalty.
        """
        if not cluster:
            return EvidenceConfidence(
                score=0.1,
                source_weight_factor=0.0,
                cross_validation_count=0,
                freshness_factor=0.0,
                conflict_penalty=0.0,
                rationale="No evidence records available.",
            )

        # Source Credibility Component
        weights = [self.SOURCE_WEIGHTS.get(e.source, 0.65) for e in cluster]
        avg_source_weight = sum(weights) / len(weights)

        # Cross-validation factor: up to 3 independent reports saturates to 1.0
        n_count = len(cluster)
        cross_val_factor = min(1.0, 0.4 + (0.2 * n_count))

        # Freshness factor: decays slightly with elapsed minutes (simulated 1.0 for fresh)
        freshness_factor = 0.95

        # Conflict penalty
        conflict_penalty = 0.0
        for c in conflicts:
            if c.severity == "CRITICAL":
                conflict_penalty += 0.18
            elif c.severity == "HIGH":
                conflict_penalty += 0.12
            else:
                conflict_penalty += 0.06

        raw_score = (
            (avg_source_weight * 0.45)
            + (cross_val_factor * 0.35)
            + (freshness_factor * 0.20)
            - conflict_penalty
        )
        final_score = max(0.15, min(0.98, round(raw_score, 2)))

        rationale = (
            f"Sources: {n_count} reports (Avg Source Weight: {avg_source_weight:.2f}, "
            f"Cross-Val: {cross_val_factor:.2f}, Conflicts: -{conflict_penalty:.2f})"
        )

        return EvidenceConfidence(
            score=final_score,
            source_weight_factor=round(avg_source_weight, 2),
            cross_validation_count=n_count,
            freshness_factor=round(freshness_factor, 2),
            conflict_penalty=round(conflict_penalty, 2),
            rationale=rationale,
        )

    def process_evidence(self, raw_reports: List[RawEvidence]) -> List[Incident]:
        """
        Full Pipeline: Ingests raw evidence, clusters incidents, detects conflicts,
        and generates verified aggregated Incident records.
        """
        clusters = self.cluster_evidence(raw_reports)
        incidents: List[Incident] = []

        for idx, cluster in enumerate(clusters):
            cluster_id = f"CLUSTER-{idx + 1:02d}"
            conflicts = self.detect_conflicts(cluster)
            confidence = self.calculate_confidence(cluster, conflicts)

            # Center coordinates
            avg_lat = sum(e.latitude for e in cluster) / len(cluster)
            avg_lon = sum(e.longitude for e in cluster) / len(cluster)

            # Casualties
            cas_values = [e.reported_casualties for e in cluster]
            max_cas = max(cas_values) if cas_values else 0
            avg_cas = int(round(sum(cas_values) / len(cas_values))) if cas_values else 0
            cas_range = f"{min(cas_values)} - {max_cas} reported" if len(cluster) > 1 else f"{max_cas} reported"

            # Road status: conservative safety rule - if any sensor or scout reports blocked, mark blocked
            blocked_types = {RoadStatus.COLLAPSED, RoadStatus.SUBMERGED, RoadStatus.BLOCKED}
            verified_road = RoadStatus.PASSABLE
            for e in cluster:
                if e.road_status in blocked_types:
                    verified_road = e.road_status
                    break
                elif e.road_status == RoadStatus.WATERLOGGED:
                    verified_road = RoadStatus.WATERLOGGED

            # Water depth: take authoritative sensor or max
            sensor_depths = [e.water_depth_m for e in cluster if e.source == SourceType.IOT_SENSOR]
            verified_depth = max(sensor_depths) if sensor_depths else (max([e.water_depth_m for e in cluster]) if cluster else 0.0)

            title = f"{cluster[0].hazard_type.capitalize()} Crisis @ Cluster #{idx + 1}"
            landmark = cluster[0].description[:45]

            incident = Incident(
                id=f"INC-{idx + 1:03d}",
                cluster_id=cluster_id,
                title=title,
                hazard_type=cluster[0].hazard_type,
                latitude=round(avg_lat, 5),
                longitude=round(avg_lon, 5),
                address_or_landmark=landmark,
                aggregated_casualties=max(avg_cas, max_cas),
                casualty_range=cas_range,
                verified_road_status=verified_road,
                verified_water_depth_m=round(verified_depth, 2),
                confidence=confidence,
                conflicts=conflicts,
                evidence_list=cluster,
                status="ACTIVE",
            )
            incidents.append(incident)

        return incidents
