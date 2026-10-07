import React, { useState, useEffect } from 'react';
import { ShieldAlert, Activity, Clock, AlertTriangle, Users, Compass } from 'lucide-react';
import { EOCState } from '../types';

interface HeaderProps {
  state: EOCState | null;
}

export const Header: React.FC<HeaderProps> = ({ state }) => {
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString() + ' IST');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const totalStranded = state?.zones.reduce((acc, z) => acc + z.estimated_stranded_count, 0) || 0;
  const criticalCount = state?.zones.filter(z => z.triage_level === 'CRITICAL_P1').length || 0;
  const activeUnits = state?.resources.filter(r => r.status === 'EN_ROUTE' || r.status === 'ON_SCENE').length || 0;

  return (
    <header className="bg-eoc-darkest border-b border-eoc-border px-4 py-2 flex flex-col md:flex-row items-center justify-between gap-3 shrink-0">
      {/* Brand & Designation */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded bg-cyan-950/60 border border-eoc-accent flex items-center justify-center text-eoc-accent shadow-glow-cyan">
          <ShieldAlert className="w-5 h-5 animate-pulse" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-mono font-bold text-base tracking-wider text-white">
              RESQ-AI <span className="text-eoc-accent text-xs font-normal">v1.0-DEMO</span>
            </h1>
            <span className="bg-amber-500/10 border border-amber-500/30 text-amber-400 text-[10px] px-2 py-0.5 rounded font-mono font-semibold tracking-wide">
              SIMULATION DATASET
            </span>
          </div>
          <p className="text-[11px] text-slate-400">
            Adaptive Emergency Decision & Resource Replanning Engine // EOC Ops
          </p>
        </div>
      </div>

      {/* KPI Tickers */}
      <div className="flex items-center gap-4 text-xs font-mono">
        <div className="bg-eoc-panel border border-eoc-border px-3 py-1 rounded flex items-center gap-2">
          <Users className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-slate-400">Stranded:</span>
          <span className="text-white font-bold">{totalStranded}</span>
        </div>

        <div className="bg-eoc-panel border border-eoc-border px-3 py-1 rounded flex items-center gap-2">
          <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />
          <span className="text-slate-400">P1 Crises:</span>
          <span className="text-rose-400 font-bold">{criticalCount}</span>
        </div>

        <div className="bg-eoc-panel border border-eoc-border px-3 py-1 rounded flex items-center gap-2">
          <Compass className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-slate-400">Mobilized:</span>
          <span className="text-emerald-400 font-bold">{activeUnits} / {state?.resources.length || 8}</span>
        </div>

        <div className="bg-eoc-panel border border-eoc-border px-3 py-1 rounded flex items-center gap-2 text-slate-300">
          <Clock className="w-3.5 h-3.5 text-eoc-accent" />
          <span className="font-semibold">{timeStr}</span>
        </div>
      </div>
    </header>
  );
};
