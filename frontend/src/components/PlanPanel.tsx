import React from 'react';
import { Truck, GitCommit, ArrowRight, Eye, ShieldCheck, RefreshCw, AlertCircle } from 'lucide-react';
import { ResourcePlan, PlanDiff, AllocationDecision } from '../types';

interface PlanPanelProps {
  plan: ResourcePlan | null;
  diff: PlanDiff | null;
  currentAct: number;
  onInspectDecision: (decision: AllocationDecision) => void;
  onOpenDiffModal: () => void;
  onOpenOverride: (decision: AllocationDecision) => void;
}

export const PlanPanel: React.FC<PlanPanelProps> = ({
  plan,
  diff,
  currentAct,
  onInspectDecision,
  onOpenDiffModal,
  onOpenOverride,
}) => {
  if (!plan) {
    return (
      <div className="bg-eoc-darkest border border-eoc-border rounded-lg p-4 text-center text-slate-500 font-mono text-xs">
        No active allocation plan formulated yet.
      </div>
    );
  }

  return (
    <div className="bg-eoc-darkest border border-eoc-border rounded-lg flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="bg-eoc-panel border-b border-eoc-border px-3 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Truck className="w-4 h-4 text-eoc-accent" />
          <span className="font-mono font-bold text-xs text-white uppercase tracking-wider">
            Resource Allocation Plan
          </span>
          <span className="bg-cyan-950 border border-cyan-800 text-cyan-300 font-mono text-[10px] px-1.5 py-0.2 rounded font-bold">
            v{plan.plan_version}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {diff && (
            <button
              onClick={onOpenDiffModal}
              className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/50 text-amber-300 font-mono text-[10px] font-semibold animate-pulse shadow-glow-cyan"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Old vs New Plan Diff</span>
            </button>
          )}

          <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
            plan.status === 'APPROVED'
              ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
              : 'bg-amber-950 text-amber-400 border border-amber-800'
          }`}>
            {plan.status}
          </span>
        </div>
      </div>

      {/* Replan Alert Banner if in Act 2 */}
      {diff && (
        <div className="bg-amber-950/40 border-b border-amber-500/40 px-3 py-2 flex items-center justify-between text-xs font-mono">
          <div className="flex items-center gap-2 text-amber-300">
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
            <span className="truncate">
              <strong>Dynamic Replan:</strong> {diff.trigger_event_title} ({diff.diverted_count} units diverted)
            </span>
          </div>
          <button
            onClick={onOpenDiffModal}
            className="text-[11px] underline text-cyan-400 hover:text-cyan-300 font-semibold shrink-0 ml-2"
          >
            Review Diff
          </button>
        </div>
      )}

      {/* Plan Summary Ticker */}
      <div className="bg-eoc-surface/60 border-b border-eoc-border px-3 py-1.5 grid grid-cols-2 text-[11px] font-mono text-slate-300">
        <div>
          Avg Response ETA: <strong className="text-white">{plan.total_avg_eta_minutes} min</strong>
        </div>
        <div className="text-right">
          Lives Protected: <strong className="text-emerald-400">{plan.total_estimated_lives_protected}</strong>
        </div>
      </div>

      {/* Allocation Decision Cards */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {plan.decisions.map((decision) => (
          <div
            key={decision.id}
            className="bg-eoc-panel border border-eoc-border hover:border-slate-600 rounded-md p-2.5 space-y-2 text-xs transition-all"
          >
            {/* Top row: Resource -> Target Zone */}
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 font-mono">
                <span className="bg-cyan-500/20 text-eoc-accent border border-cyan-500/40 px-1.5 py-0.5 rounded font-bold text-[11px]">
                  {decision.resource_code}
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                <span className="font-semibold text-white truncate max-w-[150px] sm:max-w-[200px]">
                  {decision.target_zone_name}
                </span>
              </div>

              <div className="shrink-0 font-mono text-right">
                <span className="text-[11px] text-amber-400 font-bold">
                  ETA: {decision.eta_minutes}m
                </span>
              </div>
            </div>

            {/* Matched Capabilities */}
            <div className="flex items-center gap-1.5 font-mono text-[10px]">
              <span className="text-slate-400">Matched:</span>
              <div className="flex flex-wrap gap-1">
                {decision.matched_capabilities.map((cap) => (
                  <span
                    key={cap}
                    className="bg-slate-800 text-cyan-300 px-1 py-0.2 rounded border border-slate-700"
                  >
                    {cap}
                  </span>
                ))}
              </div>
            </div>

            {/* High-level reasoning snippet */}
            <p className="text-[11px] text-slate-300 line-clamp-2 leading-relaxed">
              {decision.explanation_why_this_unit}
            </p>

            {/* Buttons: Inspect Reasoning & Commander Override */}
            <div className="flex items-center justify-between pt-1 border-t border-slate-800 font-mono text-[10px]">
              <button
                onClick={() => onInspectDecision(decision)}
                className="flex items-center gap-1 text-eoc-accent hover:underline py-0.5"
              >
                <Eye className="w-3 h-3" />
                <span>Decision Trace (Why this unit?)</span>
              </button>

              <button
                onClick={() => onOpenOverride(decision)}
                className="text-slate-400 hover:text-amber-400 py-0.5"
              >
                Commander Override
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
