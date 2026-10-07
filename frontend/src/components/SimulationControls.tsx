import React from 'react';
import { Play, Flame, CheckCircle, RotateCcw, AlertOctagon, ArrowRight } from 'lucide-react';
import { EOCState } from '../types';

interface SimulationControlsProps {
  state: EOCState | null;
  onTriggerAct2: () => void;
  onOpenApproval: () => void;
  onReset: () => void;
  isLoading: boolean;
}

export const SimulationControls: React.FC<SimulationControlsProps> = ({
  state,
  onTriggerAct2,
  onOpenApproval,
  onReset,
  isLoading,
}) => {
  const currentAct = state?.current_act || 1;

  return (
    <div className="bg-eoc-darkest border-b border-eoc-border px-4 py-2 flex flex-wrap items-center justify-between gap-3">
      {/* Simulation Stage Navigator */}
      <div className="flex items-center gap-2 text-xs font-mono">
        <span className="text-slate-400 font-semibold uppercase tracking-wider text-[11px] mr-1">
          Demo Workflow:
        </span>

        {/* Act 1 Pill */}
        <div
          className={`flex items-center gap-1.5 px-3 py-1 rounded border transition-all ${
            currentAct === 1
              ? 'bg-cyan-950/80 border-eoc-accent text-eoc-accent shadow-glow-cyan'
              : 'bg-eoc-panel border-eoc-border text-slate-400'
          }`}
        >
          <span className="w-4 h-4 rounded-full bg-cyan-500/20 text-center text-[10px] leading-4 font-bold">1</span>
          <span>Act I: Evidence Influx</span>
        </div>

        <ArrowRight className="w-3.5 h-3.5 text-slate-600" />

        {/* Act 2 Pill */}
        <div
          className={`flex items-center gap-1.5 px-3 py-1 rounded border transition-all ${
            currentAct === 2
              ? 'bg-rose-950/80 border-rose-500 text-rose-300 shadow-glow-danger'
              : 'bg-eoc-panel border-eoc-border text-slate-400'
          }`}
        >
          <span className="w-4 h-4 rounded-full bg-rose-500/20 text-center text-[10px] leading-4 font-bold">2</span>
          <span>Act II: Shock & Replan</span>
        </div>

        <ArrowRight className="w-3.5 h-3.5 text-slate-600" />

        {/* Act 3 Pill */}
        <div
          className={`flex items-center gap-1.5 px-3 py-1 rounded border transition-all ${
            currentAct === 3
              ? 'bg-emerald-950/80 border-emerald-500 text-emerald-300 shadow-glow-success'
              : 'bg-eoc-panel border-eoc-border text-slate-400'
          }`}
        >
          <span className="w-4 h-4 rounded-full bg-emerald-500/20 text-center text-[10px] leading-4 font-bold">3</span>
          <span>Act III: Commander Dispatch</span>
        </div>
      </div>

      {/* Action Buttons for Jury Demo */}
      <div className="flex items-center gap-2">
        {/* Act 2 Injector Button */}
        {currentAct === 1 && (
          <button
            onClick={onTriggerAct2}
            disabled={isLoading}
            className="flex items-center gap-2 px-3 py-1.5 rounded bg-rose-600 hover:bg-rose-500 text-white text-xs font-mono font-semibold shadow-glow-danger transition-all disabled:opacity-50"
          >
            <Flame className="w-3.5 h-3.5 animate-bounce" />
            <span>Inject Act II Shock Event</span>
          </button>
        )}

        {/* Act 3 Approval Button */}
        {currentAct === 2 && (
          <button
            onClick={onOpenApproval}
            disabled={isLoading}
            className="flex items-center gap-2 px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-mono font-semibold shadow-glow-success transition-all disabled:opacity-50"
          >
            <CheckCircle className="w-3.5 h-3.5" />
            <span>Review & Authorize Replan</span>
          </button>
        )}

        {/* Plan Status Badge if approved */}
        {currentAct === 3 && (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded bg-emerald-900/40 border border-emerald-500/50 text-emerald-300 text-xs font-mono">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            <span>DISPATCH AUTHORIZED // TELEMETRY ACTIVE</span>
          </div>
        )}

        {/* Reset Button */}
        <button
          onClick={onReset}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded bg-eoc-panel hover:bg-slate-800 border border-eoc-border text-slate-300 hover:text-white text-xs font-mono transition-all"
          title="Reset Simulation to Act I Baseline"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Reset</span>
        </button>
      </div>
    </div>
  );
};
