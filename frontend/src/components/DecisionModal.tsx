import React from 'react';
import { X, CheckCircle2, XCircle, ShieldCheck, Compass, Info } from 'lucide-react';
import { AllocationDecision, CriticalZone } from '../types';

interface DecisionModalProps {
  decision: AllocationDecision | null;
  zone: CriticalZone | null;
  onClose: () => void;
}

export const DecisionModal: React.FC<DecisionModalProps> = ({
  decision,
  zone,
  onClose,
}) => {
  if (!decision && !zone) return null;

  return (
    <div className="fixed inset-0 z-[2000] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-eoc-panel border border-cyan-500/40 rounded-lg max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden font-sans">
        {/* Header */}
        <div className="bg-eoc-darkest border-b border-eoc-border px-5 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Compass className="w-5 h-5 text-eoc-accent" />
            <h2 className="font-mono font-bold text-sm text-white">
              {decision ? 'DECISION TRACE & EXPLAINABILITY LOG' : 'CRITICAL ZONE MATHEMATICAL BREAKDOWN'}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs">
          {decision && (
            <>
              {/* Decision Target */}
              <div className="bg-eoc-darkest p-3 rounded-md border border-eoc-border font-mono">
                <span className="text-slate-500 text-[10px] block">DISPATCH VECTOR:</span>
                <div className="text-sm font-bold text-white flex items-center gap-2 mt-0.5">
                  <span className="text-cyan-400">{decision.resource_code}</span>
                  <span className="text-slate-500">➔</span>
                  <span className="text-amber-400">{decision.target_zone_name}</span>
                  <span className="text-[10px] bg-rose-500/20 text-rose-300 border border-rose-500/40 px-1.5 py-0.2 rounded">
                    {decision.target_zone_triage}
                  </span>
                </div>
              </div>

              {/* Primary Reasoning */}
              <div className="space-y-1.5">
                <div className="font-mono font-bold text-slate-300 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Why This Unit Was Selected?</span>
                </div>
                <div className="bg-eoc-surface/60 border border-slate-800 p-3 rounded text-slate-200 leading-relaxed">
                  {decision.explanation_why_this_unit}
                </div>
              </div>

              {/* Alternative Considered */}
              <div className="space-y-1.5">
                <div className="font-mono font-bold text-slate-300 flex items-center gap-1.5">
                  <XCircle className="w-4 h-4 text-amber-400" />
                  <span>Alternative Considered & Trade-Off Reason:</span>
                </div>
                <div className="bg-eoc-surface/60 border border-slate-800 p-3 rounded text-slate-300 leading-relaxed">
                  {decision.alternative_rejected}
                </div>
              </div>

              {/* Verified Constraints */}
              <div className="space-y-1.5">
                <div className="font-mono font-bold text-slate-300 flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-cyan-400" />
                  <span>Operational Constraints Satisfied:</span>
                </div>
                <div className="space-y-1">
                  {decision.constraints_satisfied.map((c, i) => (
                    <div
                      key={i}
                      className="bg-eoc-darkest border border-eoc-border px-2.5 py-1.5 rounded font-mono text-[11px] text-cyan-300 flex items-center gap-2"
                    >
                      <span className="text-emerald-400">✓</span>
                      <span>{c}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {zone && zone.score_breakdown && (
            <div className="space-y-4">
              <div className="bg-eoc-darkest p-3 rounded border border-eoc-border">
                <div className="font-mono text-sm font-bold text-white mb-1">
                  {zone.name} ({zone.code})
                </div>
                <div className="font-mono text-xs text-amber-400 font-bold">
                  Final Calculated Priority Score: {zone.priority_score.toFixed(1)} / 100 ({zone.triage_level})
                </div>
              </div>

              {/* Formula String */}
              <div className="bg-eoc-surface/60 p-3 rounded border border-cyan-500/30 font-mono text-[11px]">
                <span className="text-slate-400 block text-[10px] mb-1">MATHEMATICAL FORMULA EVALUATION:</span>
                <span className="text-cyan-300 font-bold">
                  {zone.score_breakdown.calculated_formula}
                </span>
              </div>

              {/* Component Weights Table */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-[11px]">
                <div className="bg-eoc-darkest p-2 rounded border border-eoc-border">
                  <span className="text-slate-500 block text-[10px]">Urgency (x4.0):</span>
                  <span className="text-white font-bold">{zone.score_breakdown.urgency_weighted} pts</span>
                </div>
                <div className="bg-eoc-darkest p-2 rounded border border-eoc-border">
                  <span className="text-slate-500 block text-[10px]">Severity (x4.0):</span>
                  <span className="text-white font-bold">{zone.score_breakdown.severity_weighted} pts</span>
                </div>
                <div className="bg-eoc-darkest p-2 rounded border border-eoc-border">
                  <span className="text-slate-500 block text-[10px]">Vulnerability (x4.0):</span>
                  <span className="text-white font-bold">{zone.score_breakdown.vulnerability_weighted} pts</span>
                </div>
                <div className="bg-eoc-darkest p-2 rounded border border-eoc-border">
                  <span className="text-slate-500 block text-[10px]">Friction & Conf:</span>
                  <span className="text-cyan-400 font-bold">Acc {zone.score_breakdown.accessibility_factor} | C_ev {zone.score_breakdown.evidence_confidence}</span>
                </div>
              </div>

              <div className="bg-slate-900/80 p-3 rounded border border-slate-800 text-slate-300 leading-relaxed text-[11px]">
                <Info className="w-3.5 h-3.5 text-cyan-400 inline mr-1" />
                {zone.score_breakdown.explanation}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-eoc-darkest border-t border-eoc-border px-5 py-3 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-semibold"
          >
            Close Trace
          </button>
        </div>
      </div>
    </div>
  );
};
