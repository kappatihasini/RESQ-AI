import React from 'react';
import { AlertCircle, ChevronRight, Calculator, Waves, Users, Zap } from 'lucide-react';
import { CriticalZone } from '../types';

interface ZonePriorityListProps {
  zones: CriticalZone[];
  selectedZone: CriticalZone | null;
  onSelectZone: (zone: CriticalZone) => void;
  onExplainZone: (zone: CriticalZone) => void;
}

export const ZonePriorityList: React.FC<ZonePriorityListProps> = ({
  zones,
  selectedZone,
  onSelectZone,
  onExplainZone,
}) => {
  return (
    <div className="bg-eoc-darkest border border-eoc-border rounded-lg flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="bg-eoc-panel border-b border-eoc-border px-3 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-500" />
          <span className="font-mono font-bold text-xs text-white uppercase tracking-wider">
            Critical-Zone Prioritization
          </span>
        </div>
        <span className="text-[10px] font-mono text-slate-400">
          Ranked by Explainable Formula
        </span>
      </div>

      {/* Zone Items */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
        {zones.map((zone, index) => {
          const isSelected = selectedZone?.id === zone.id;
          const triageStyles: Record<string, { border: string; bg: string; text: string; badge: string }> = {
            CRITICAL_P1: {
              border: 'border-rose-500/70',
              bg: 'bg-rose-950/20 hover:bg-rose-950/30',
              text: 'text-rose-400',
              badge: 'bg-rose-500 text-white',
            },
            HIGH_P2: {
              border: 'border-amber-500/70',
              bg: 'bg-amber-950/20 hover:bg-amber-950/30',
              text: 'text-amber-400',
              badge: 'bg-amber-500 text-white',
            },
            MEDIUM_P3: {
              border: 'border-yellow-500/70',
              bg: 'bg-yellow-950/20 hover:bg-yellow-950/30',
              text: 'text-yellow-400',
              badge: 'bg-yellow-500 text-white',
            },
            LOW_P4: {
              border: 'border-emerald-500/70',
              bg: 'bg-emerald-950/20 hover:bg-emerald-950/30',
              text: 'text-emerald-400',
              badge: 'bg-emerald-500 text-white',
            },
          };

          const style = triageStyles[zone.triage_level] || triageStyles.MEDIUM_P3;

          return (
            <div
              key={zone.id}
              onClick={() => onSelectZone(zone)}
              className={`p-3 rounded-md border transition-all cursor-pointer ${
                isSelected
                  ? 'border-eoc-accent bg-cyan-950/30 shadow-glow-cyan'
                  : `${style.border} ${style.bg}`
              }`}
            >
              {/* Top Row: Rank, Code, Triage & Score */}
              <div className="flex items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-slate-500">
                    #{index + 1}
                  </span>
                  <span className="font-mono font-bold text-xs text-white">
                    {zone.code}
                  </span>
                  <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded ${style.badge}`}>
                    {zone.triage_level}
                  </span>
                </div>

                <div className="flex items-center gap-2 font-mono">
                  <span className="text-[10px] text-slate-400">Score:</span>
                  <span className={`font-bold text-sm ${style.text}`}>
                    {zone.priority_score.toFixed(1)}
                  </span>
                </div>
              </div>

              {/* Zone Name */}
              <div className="text-xs font-medium text-slate-200 mb-2 truncate">
                {zone.name}
              </div>

              {/* Progress Bar of Score */}
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-2">
                <div
                  className={`h-full transition-all duration-500 ${
                    zone.priority_score >= 80 ? 'bg-rose-500' :
                    zone.priority_score >= 60 ? 'bg-amber-500' :
                    zone.priority_score >= 40 ? 'bg-yellow-500' : 'bg-emerald-500'
                  }`}
                  style={{ width: `${Math.min(100, zone.priority_score)}%` }}
                />
              </div>

              {/* Metadata Indicators */}
              <div className="grid grid-cols-3 gap-1 font-mono text-[10px] text-slate-300 mb-2">
                <div className="bg-eoc-surface px-1.5 py-0.5 rounded flex items-center gap-1 border border-eoc-border">
                  <Users className="w-3 h-3 text-amber-400" />
                  <span>~{zone.estimated_stranded_count}</span>
                </div>
                <div className="bg-eoc-surface px-1.5 py-0.5 rounded flex items-center gap-1 border border-eoc-border">
                  <Waves className="w-3 h-3 text-cyan-400" />
                  <span>{zone.water_level_m}m</span>
                </div>
                <div className="bg-eoc-surface px-1.5 py-0.5 rounded flex items-center gap-1 border border-eoc-border">
                  <Zap className="w-3 h-3 text-yellow-400" />
                  <span className="truncate">{zone.power_status}</span>
                </div>
              </div>

              {/* Capabilities & Explain Button */}
              <div className="flex items-center justify-between pt-1 border-t border-slate-800/80">
                <div className="flex flex-wrap gap-1">
                  {zone.required_capabilities.slice(0, 2).map((cap) => (
                    <span
                      key={cap}
                      className="bg-slate-800 text-slate-300 text-[9px] font-mono px-1 py-0.2 rounded"
                    >
                      {cap}
                    </span>
                  ))}
                  {zone.required_capabilities.length > 2 && (
                    <span className="text-[9px] text-slate-500 font-mono">
                      +{zone.required_capabilities.length - 2}
                    </span>
                  )}
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onExplainZone(zone);
                  }}
                  className="flex items-center gap-1 text-[10px] font-mono text-eoc-accent hover:underline bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/60"
                >
                  <Calculator className="w-3 h-3" />
                  <span>Explain Math</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
