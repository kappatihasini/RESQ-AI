import React from 'react';
import { X, RefreshCw, ArrowRight, AlertTriangle, ShieldCheck, CheckCircle } from 'lucide-react';
import { PlanDiff } from '../types';

interface PlanDiffModalProps {
  diff: PlanDiff | null;
  onClose: () => void;
  onApproveReplan: () => void;
}

export const PlanDiffModal: React.FC<PlanDiffModalProps> = ({
  diff,
  onClose,
  onApproveReplan,
}) => {
  if (!diff) return null;

  return (
    <div className="fixed inset-0 z-[2000] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-eoc-panel border border-cyan-500/50 rounded-lg max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden font-sans">
        {/* Modal Header */}
        <div className="bg-eoc-darkest border-b border-eoc-border px-5 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-amber-500/20 border border-amber-500 flex items-center justify-center text-amber-400">
              <RefreshCw className="w-4 h-4 animate-spin" />
            </div>
            <div>
              <h2 className="font-mono font-bold text-sm text-white flex items-center gap-2">
                DYNAMIC REPLANNING DIFFERENTIAL
                <span className="bg-amber-500 text-black text-[10px] px-2 py-0.5 rounded font-black tracking-wider">
                  OLD PLAN VS NEW PLAN
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Automated re-optimization triggered by environmental delta event
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Trigger Event Banner */}
        <div className="bg-rose-950/40 border-b border-rose-500/30 px-5 py-3 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
          <div className="text-xs">
            <div className="font-mono font-bold text-rose-300">
              TRIGGER EVENT: {diff.trigger_event_title}
            </div>
            <p className="text-slate-300 mt-0.5 leading-relaxed">
              {diff.trigger_event_description}
            </p>
          </div>
        </div>

        {/* Diff KPI Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 bg-eoc-surface/40 border-b border-eoc-border text-xs font-mono">
          <div className="bg-eoc-darkest p-3 rounded border border-eoc-border">
            <span className="text-slate-400 text-[11px] block">Critical Diverted Units:</span>
            <span className="text-amber-400 text-lg font-bold">
              {diff.diverted_count} Units Redirected
            </span>
          </div>

          <div className="bg-eoc-darkest p-3 rounded border border-eoc-border">
            <span className="text-slate-400 text-[11px] block">Reserve Activations:</span>
            <span className="text-emerald-400 text-lg font-bold">
              +{diff.newly_assigned_count} Mobilized
            </span>
          </div>

          <div className="bg-eoc-darkest p-3 rounded border border-eoc-border">
            <span className="text-slate-400 text-[11px] block">Decision Latency:</span>
            <span className="text-cyan-400 text-lg font-bold">&lt; 35 ms</span>
          </div>
        </div>

        {/* Side-by-Side Changes Table */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          <h3 className="font-mono text-xs font-bold text-slate-300 uppercase tracking-wider">
            Differential Allocation Trace
          </h3>

          <div className="space-y-2 font-mono text-xs">
            {diff.changes.map((item, index) => (
              <div
                key={index}
                className="bg-eoc-darkest border border-eoc-border rounded-md p-3 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 px-2 py-0.5 rounded font-bold">
                      {item.resource_code}
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      item.change_type === 'DIVERTED'
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50'
                        : item.change_type === 'RE-ROUTED'
                        ? 'bg-blue-500/20 text-blue-300 border border-blue-500/50'
                        : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/50'
                    }`}>
                      {item.change_type}
                    </span>
                  </div>
                </div>

                {/* Old vs New Vector */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] bg-eoc-surface/60 p-2 rounded border border-slate-800">
                  <div>
                    <span className="text-slate-500 block text-[10px]">PREVIOUS ASSIGNMENT (OLD PLAN):</span>
                    <span className="text-slate-300 font-medium">
                      {item.old_zone_name || 'Reserve Standby'}
                    </span>
                    {item.old_eta && (
                      <span className="text-slate-500 text-[10px] ml-2">({item.old_eta}m ETA)</span>
                    )}
                  </div>

                  <div>
                    <span className="text-slate-500 block text-[10px]">NEW ASSIGNMENT (NEW REPLAN):</span>
                    <span className="text-emerald-400 font-medium">
                      {item.new_zone_name || 'Reserve Standby'}
                    </span>
                    {item.new_eta && (
                      <span className="text-cyan-400 text-[10px] ml-2">({item.new_eta}m ETA)</span>
                    )}
                  </div>
                </div>

                {/* Justification */}
                <p className="text-[11px] text-slate-300 font-sans leading-relaxed">
                  <strong className="text-amber-400 font-mono">Replanning Justification: </strong>
                  {item.reason}
                </p>
              </div>
            ))}
          </div>

          {/* Trade-off Impact Analysis */}
          <div className="bg-emerald-950/20 border border-emerald-500/30 rounded-md p-3 text-xs space-y-1">
            <div className="font-mono font-bold text-emerald-400 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Ethical & Mathematical Trade-Off Assessment</span>
            </div>
            <p className="text-slate-300 text-[11px] leading-relaxed">
              {diff.lives_risk_delta_explanation}
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="bg-eoc-darkest border-t border-eoc-border px-5 py-3 flex items-center justify-between">
          <span className="text-[11px] font-mono text-slate-400">
            Pending Commander Authorization Gate
          </span>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono transition-all"
            >
              Dismiss View
            </button>
            <button
              onClick={() => {
                onClose();
                onApproveReplan();
              }}
              className="px-4 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-mono font-semibold flex items-center gap-2 shadow-glow-success transition-all"
            >
              <CheckCircle className="w-4 h-4" />
              <span>Proceed to Commander Authorization</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
