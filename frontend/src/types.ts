export interface RawEvidence {
  id: string;
  source: 'CITIZEN_SOS' | 'FIELD_DRONE' | 'IOT_SENSOR' | 'EOC_DISPATCH';
  timestamp: string;
  latitude: float;
  longitude: float;
  description: string;
  reported_casualties: number;
  road_status: 'PASSABLE' | 'SLOW_TRAFFIC' | 'WATERLOGGED' | 'BLOCKED' | 'SUBMERGED' | 'COLLAPSED';
  water_depth_m: number;
  hazard_type: string;
}

type float = number;

export interface Conflict {
  id: string;
  conflict_type: string;
  evidence_ids: string[];
  description: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  resolution_status: string;
  resolution_note?: string;
}

export interface EvidenceConfidence {
  score: number;
  source_weight_factor: number;
  cross_validation_count: number;
  freshness_factor: number;
  conflict_penalty: number;
  rationale: string;
}

export interface Incident {
  id: string;
  cluster_id: string;
  title: string;
  hazard_type: string;
  latitude: number;
  longitude: number;
  address_or_landmark: string;
  aggregated_casualties: number;
  casualty_range: string;
  verified_road_status: string;
  verified_water_depth_m: number;
  confidence: EvidenceConfidence;
  conflicts: Conflict[];
  evidence_list: RawEvidence[];
  status: string;
}

export interface ScoreBreakdown {
  urgency_raw: number;
  urgency_weighted: number;
  severity_raw: number;
  severity_weighted: number;
  vulnerability_raw: number;
  vulnerability_weighted: number;
  accessibility_factor: number;
  evidence_confidence: number;
  calculated_formula: string;
  explanation: string;
}

export interface CriticalZone {
  id: string;
  name: string;
  code: string;
  center_lat: number;
  center_lon: number;
  radius_meters: number;
  urgency: number;
  severity: number;
  vulnerability: number;
  accessibility_factor: number;
  priority_score: number;
  triage_level: 'CRITICAL_P1' | 'HIGH_P2' | 'MEDIUM_P3' | 'LOW_P4';
  score_breakdown?: ScoreBreakdown;
  required_capabilities: string[];
  estimated_stranded_count: number;
  water_level_m: number;
  power_status: string;
  status: string;
}

export interface EmergencyResource {
  id: string;
  code: string;
  name: string;
  type: string;
  capabilities: string[];
  base_station: string;
  current_lat: number;
  current_lon: number;
  capacity_persons: number;
  speed_kmh: number;
  status: 'AVAILABLE' | 'EN_ROUTE' | 'ON_SCENE' | 'COMMITTED' | 'MAINTENANCE';
  current_assigned_zone_id?: string;
  estimated_arrival_minutes?: number;
  is_amphibious_or_air: boolean;
}

export interface AllocationDecision {
  id: string;
  resource_id: string;
  resource_code: string;
  resource_type: string;
  target_zone_id: string;
  target_zone_name: string;
  target_zone_triage: string;
  distance_km: number;
  eta_minutes: number;
  matched_capabilities: string[];
  capacity_contributed: number;
  score_impact: number;
  explanation_why_this_unit: string;
  alternative_rejected: string;
  constraints_satisfied: string[];
  status: 'PROPOSED' | 'APPROVED' | 'OVERRIDDEN' | 'REJECTED';
  commander_override_reason?: string;
}

export interface ResourcePlan {
  id: string;
  plan_version: number;
  created_at: string;
  status: 'PROPOSED' | 'APPROVED' | 'SUPERSEDED';
  decisions: AllocationDecision[];
  unassigned_resource_ids: string[];
  unserved_zone_ids: string[];
  total_estimated_lives_protected: number;
  total_avg_eta_minutes: number;
  strategic_summary: string;
  is_replan: boolean;
  trigger_event?: string;
}

export interface PlanDiffItem {
  resource_id: string;
  resource_code: string;
  old_zone_id?: string;
  old_zone_name?: string;
  new_zone_id?: string;
  new_zone_name?: string;
  old_eta?: number;
  new_eta?: number;
  change_type: 'DIVERTED' | 'RE-ROUTED' | 'NEWLY_ASSIGNED' | 'RELEASED';
  reason: string;
}

export interface PlanDiff {
  id: string;
  timestamp: string;
  old_plan_id: string;
  new_plan_id: string;
  trigger_event_title: string;
  trigger_event_description: string;
  changes: PlanDiffItem[];
  diverted_count: number;
  newly_assigned_count: number;
  lives_risk_delta_explanation: string;
  executive_diff_summary: string;
}

export interface EOCState {
  current_act: number;
  act_title: string;
  act_description: string;
  is_simulation: boolean;
  simulation_disclaimer: string;
  raw_evidence_count: number;
  incidents: Incident[];
  conflicts: Conflict[];
  zones: CriticalZone[];
  resources: EmergencyResource[];
  current_plan: ResourcePlan;
  plans_history_count: number;
  latest_diff?: PlanDiff;
  audit_log: Array<{
    timestamp: string;
    action: string;
    actor: string;
    details: string;
    notes?: string;
  }>;
}
