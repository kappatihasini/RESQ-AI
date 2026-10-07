import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { SimulationControls } from './components/SimulationControls';
import { TacticalMap } from './components/TacticalMap';
import { EvidenceFeed } from './components/EvidenceFeed';
import { ZonePriorityList } from './components/ZonePriorityList';
import { PlanPanel } from './components/PlanPanel';
import { PlanDiffModal } from './components/PlanDiffModal';
import { DecisionModal } from './components/DecisionModal';
import { CommanderModal } from './components/CommanderModal';

import {
  fetchEOCState,
  triggerAct2Shock,
  approvePlan,
  resetSimulation,
  overrideDecision,
} from './api';
import { EOCState, CriticalZone, AllocationDecision } from './types';

export const App: React.FC = () => {
  const [state, setState] = useState<EOCState | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Modal States
  const [selectedZone, setSelectedZone] = useState<CriticalZone | null>(null);
  const [inspectDecision, setInspectDecision] = useState<AllocationDecision | null>(null);
  const [explainZone, setExplainZone] = useState<CriticalZone | null>(null);
  const [showDiffModal, setShowDiffModal] = useState<boolean>(false);
  const [showApprovalModal, setShowApprovalModal] = useState<boolean>(false);
  const [overrideTarget, setOverrideTarget] = useState<AllocationDecision | null>(null);

  const loadState = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchEOCState();
      setState(data);
      setError(null);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to connect to RESQ-AI backend engine.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadState();
  }, [loadState]);

  // Handler for Act 2 Shock
  const handleTriggerAct2 = async () => {
    try {
      setLoading(true);
      await triggerAct2Shock();
      await loadState();
      setShowDiffModal(true); // Automatically show Old vs New Plan diff on shock!
    } catch (err: any) {
      alert(`Error triggering Act II: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Handler for Act 3 Approval
  const handleApprove = async (commanderName: string, notes: string) => {
    try {
      setLoading(true);
      await approvePlan(commanderName, notes);
      await loadState();
    } catch (err: any) {
      alert(`Error authorizing plan: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Handler for Reset
  const handleReset = async () => {
    try {
      setLoading(true);
      await resetSimulation();
      await loadState();
      setShowDiffModal(false);
    } catch (err: any) {
      alert(`Error resetting simulation: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Handler for Commander Override
  const handleOverride = async (
    decisionId: string,
    newResourceId: string,
    commanderName: string,
    reason: string
  ) => {
    try {
      setLoading(true);
      await overrideDecision(decisionId, newResourceId, commanderName, reason);
      await loadState();
    } catch (err: any) {
      alert(`Error overriding decision: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-[#070b12] text-slate-100 font-sans overflow-hidden bg-grid-pattern">
      {/* 1. Tactical Header */}
      <Header state={state} />

      {/* 2. Simulation Workflow Controller */}
      <SimulationControls
        state={state}
        onTriggerAct2={handleTriggerAct2}
        onOpenApproval={() => {
          setOverrideTarget(null);
          setShowApprovalModal(true);
        }}
        onReset={handleReset}
        isLoading={loading}
      />

      {/* 3. Main Tactical EOC Grid */}
      {error ? (
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="bg-rose-950/40 border border-rose-500 p-6 rounded-lg max-w-md text-center space-y-3 font-mono">
            <h3 className="text-rose-400 font-bold text-sm">EOC ENGINE DISCONNECTED</h3>
            <p className="text-xs text-slate-300">{error}</p>
            <button
              onClick={loadState}
              className="px-4 py-1.5 rounded bg-rose-600 text-white text-xs font-bold"
            >
              Retry Handshake
            </button>
          </div>
        </div>
      ) : (
        <main className="flex-1 p-3 grid grid-cols-1 lg:grid-cols-12 gap-3 min-h-0 overflow-hidden">
          {/* Left Column: Priority Zones (top) & Evidence Feed (bottom) */}
          <section className="lg:col-span-4 flex flex-col gap-3 min-h-0 h-full">
            <div className="h-1/2 min-h-0">
              <ZonePriorityList
                zones={state?.zones || []}
                selectedZone={selectedZone}
                onSelectZone={(z) => setSelectedZone(z)}
                onExplainZone={(z) => setExplainZone(z)}
              />
            </div>
            <div className="h-1/2 min-h-0">
              <EvidenceFeed
                incidents={state?.incidents || []}
                conflicts={state?.conflicts || []}
              />
            </div>
          </section>

          {/* Middle Column: Interactive Tactical Map */}
          <section className="lg:col-span-5 h-full min-h-0">
            <TacticalMap
              zones={state?.zones || []}
              resources={state?.resources || []}
              currentPlan={state?.current_plan || null}
              incidents={state?.incidents || []}
              currentAct={state?.current_act || 1}
              onSelectZone={(z) => setSelectedZone(z)}
            />
          </section>

          {/* Right Column: Resource Allocation & Dynamic Replanning */}
          <section className="lg:col-span-3 h-full min-h-0">
            <PlanPanel
              plan={state?.current_plan || null}
              diff={state?.latest_diff || null}
              currentAct={state?.current_act || 1}
              onInspectDecision={(dec) => setInspectDecision(dec)}
              onOpenDiffModal={() => setShowDiffModal(true)}
              onOpenOverride={(dec) => {
                setOverrideTarget(dec);
                setShowApprovalModal(true);
              }}
            />
          </section>
        </main>
      )}

      {/* Modals & Drawers */}
      <PlanDiffModal
        diff={showDiffModal ? state?.latest_diff || null : null}
        onClose={() => setShowDiffModal(false)}
        onApproveReplan={() => {
          setShowDiffModal(false);
          setOverrideTarget(null);
          setShowApprovalModal(true);
        }}
      />

      <DecisionModal
        decision={inspectDecision}
        zone={explainZone}
        onClose={() => {
          setInspectDecision(null);
          setExplainZone(null);
        }}
      />

      <CommanderModal
        isOpen={showApprovalModal}
        onClose={() => {
          setShowApprovalModal(false);
          setOverrideTarget(null);
        }}
        onApprove={handleApprove}
        overrideDecision={overrideTarget}
        resources={state?.resources || []}
        onOverride={handleOverride}
      />
    </div>
  );
};
