import React, { useState } from 'react';
import { Radio, AlertTriangle, Layers, CheckCircle2, ShieldCheck, MapPin } from 'lucide-react';
import { Incident, Conflict, RawEvidence } from '../types';

interface EvidenceFeedProps {
  incidents: Incident[];
  conflicts: Conflict[];
}

export const EvidenceFeed: React.FC<EvidenceFeedProps> = ({ incidents, conflicts }) => {
  const [activeTab, setActiveTab] = useState<'incidents' | 'conflicts'>('incidents');

  return (
    <div className="bg-eoc-darkest border border-eoc-border rounded-lg flex flex-col h-full overflow-hidden">
      {/* Panel Header */}
      <div className="bg-eoc-panel border-b border-eoc-border px-3 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Radio className="w-4 h-4 text-eoc-accent animate-pulse" />
          <span className="font-mono font-bold text-xs text-white uppercase tracking-wider">
            Multi-Source Intelligence Feed
          </span>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1 bg-eoc-darkest p-0.5 rounded border border-eoc-border text-[11px] font-mono">
          <button
            onClick={() => setActiveTab('incidents')}
            className={`px-2 py-0.5 rounded transition-all ${
              activeTab === 'incidents'
                ? 'bg-cyan-500/20 text-eoc-accent font-semibold border border-cyan-500/40'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Clustered ({incidents.length})
          </button>
          <button
            onClick={() => setActiveTab('conflicts')}
            className={`px-2 py-0.5 rounded transition-all flex items-center gap-1 ${
              activeTab === 'conflicts'
                ? 'bg-rose-500/20 text-rose-300 font-semibold border border-rose-500/40'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <span>Conflicts</span>
            {conflicts.length > 0 && (
              <span className="bg-rose-500 text-white rounded-full text-[9px] px-1 font-bold">
                {conflicts.length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Feed Content */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {activeTab === 'incidents' ? (
          incidents.map((inc) => (
            <div
              key={inc.id}
              className="bg-eoc-panel/80 hover:bg-eoc-panel border border-eoc-border rounded-md p-2.5 transition-all space-y-2 text-xs"
            >
              {/* Header */}
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="font-mono font-semibold text-white flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-eoc-accent shrink-0" />
                    <span>{inc.title}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 pl-5">
                    {inc.address_or_landmark}
                  </div>
                </div>
                <div className="shrink-0 text-right font-mono">
                  <span className="bg-cyan-950 border border-cyan-800/80 text-cyan-300 text-[10px] px-1.5 py-0.5 rounded font-bold">
                    C_ev: {inc.confidence.score.toFixed(2)}
                  </span>
                </div>
              </div>

              {/* Status Chips */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 font-mono text-[10px]">
                <div className="bg-eoc-surface px-2 py-1 rounded border border-eoc-border flex flex-col">
                  <span className="text-slate-400">Road Status:</span>
                  <span className={`font-semibold ${
                    inc.verified_road_status === 'PASSABLE' ? 'text-emerald-400' : 'text-rose-400'
                  }`}>
                    {inc.verified_road_status}
                  </span>
                </div>

                <div className="bg-eoc-surface px-2 py-1 rounded border border-eoc-border flex flex-col">
                  <span className="text-slate-400">Casualties:</span>
                  <span className="text-amber-400 font-semibold">{inc.casualty_range}</span>
                </div>

                <div className="bg-eoc-surface px-2 py-1 rounded border border-eoc-border flex flex-col col-span-2 sm:col-span-1">
                  <span className="text-slate-400">Water Depth:</span>
                  <span className="text-cyan-400 font-semibold">{inc.verified_water_depth_m}m</span>
                </div>
              </div>

              {/* Evidence Provenance Chain */}
              <div className="border-t border-slate-800 pt-2 space-y-1">
                <div className="text-[10px] font-mono text-slate-400 flex items-center justify-between">
                  <span>Raw Evidence Reports ({inc.evidence_list.length}):</span>
                  <span className="text-slate-500 font-mono text-[9px]">Deduplicated & Cross-Validated</span>
                </div>
                <div className="space-y-1">
                  {inc.evidence_list.map((ev) => (
                    <div
                      key={ev.id}
                      className="bg-eoc-surface/60 px-2 py-1 rounded text-[11px] flex items-start gap-1.5 text-slate-300 border border-slate-800/50"
                    >
                      <span className={`shrink-0 font-mono text-[9px] px-1 py-0.2 rounded font-bold ${
                        ev.source === 'IOT_SENSOR' ? 'bg-purple-950 text-purple-300 border border-purple-800' :
                        ev.source === 'FIELD_DRONE' ? 'bg-blue-950 text-blue-300 border border-blue-800' :
                        ev.source === 'CITIZEN_SOS' ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                        'bg-slate-800 text-slate-300'
                      }`}>
                        {ev.source}
                      </span>
                      <p className="line-clamp-2 text-[10px] flex-1">{ev.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))
        ) : (
          conflicts.map((conf) => (
            <div
              key={conf.id}
              className="bg-rose-950/20 border border-rose-500/40 rounded-md p-3 space-y-2 text-xs"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono font-bold text-rose-400 text-[11px] flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />
                  {conf.conflict_type}
                </span>
                <span className="bg-rose-500/20 border border-rose-500/50 text-rose-300 text-[9px] font-mono px-1.5 py-0.5 rounded font-bold">
                  {conf.severity}
                </span>
              </div>
              <p className="text-slate-200 text-[11px] leading-relaxed">
                {conf.description}
              </p>
              {conf.resolution_note && (
                <div className="bg-eoc-surface/90 border border-slate-800 p-2 rounded text-[10px] font-mono text-emerald-400 flex items-start gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-slate-300">Automated Resolution Rule: </strong>
                    {conf.resolution_note}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
