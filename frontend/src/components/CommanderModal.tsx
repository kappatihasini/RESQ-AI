import React, { useState } from 'react';
import { X, ShieldAlert, CheckCircle, UserCheck, AlertTriangle } from 'lucide-react';
import { AllocationDecision, EmergencyResource } from '../types';

interface CommanderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onApprove: (commanderName: string, notes: string) => void;
  overrideDecision: AllocationDecision | null;
  resources: EmergencyResource[];
  onOverride: (decisionId: string, newResourceId: string, commanderName: string, reason: string) => void;
}

export const CommanderModal: React.FC<CommanderModalProps> = ({
  isOpen,
  onClose,
  onApprove,
  overrideDecision,
  resources,
  onOverride,
}) => {
  const [commanderName, setCommanderName] = useState<string>('Commander V. Sharma');
  const [notes, setNotes] = useState<string>('Approved plan after inspecting triage priorities and capability matches.');
  const [selectedResourceId, setSelectedResourceId] = useState<string>('');
  const [overrideReason, setOverrideReason] = useState<string>('Commander tactical discretion based on on-ground radio intel.');

  if (!isOpen) return null;

  const isOverrideMode = !!overrideDecision;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isOverrideMode && overrideDecision) {
      if (!selectedResourceId) return;
      onOverride(overrideDecision.id, selectedResourceId, commanderName, overrideReason);
    } else {
      onApprove(commanderName, notes);
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[2000] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-eoc-panel border border-emerald-500/50 rounded-lg max-w-lg w-full shadow-2xl overflow-hidden font-sans">
        {/* Header */}
        <div className="bg-eoc-darkest border-b border-eoc-border px-5 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <UserCheck className="w-5 h-5 text-emerald-400" />
            <h2 className="font-mono font-bold text-sm text-white">
              {isOverrideMode ? 'COMMANDER MANUAL OVERRIDE' : 'HUMAN APPROVAL GATEWAY'}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4 text-xs">
          {/* Safety Disclaimer Banner */}
          <div className="bg-amber-950/30 border border-amber-500/40 p-3 rounded flex items-start gap-2.5 text-amber-200">
            <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div className="text-[11px] leading-relaxed">
              <strong>Human-in-the-Loop Protocol:</strong> AI provides decision support and risk modeling. Autonomous dispatch is prohibited without authenticated Commander sign-off.
            </div>
          </div>

          <div>
            <label className="font-mono font-semibold text-slate-300 block mb-1">
              Authorized EOC Incident Commander:
            </label>
            <input
              type="text"
              value={commanderName}
              onChange={(e) => setCommanderName(e.target.value)}
              className="w-full bg-eoc-darkest border border-eoc-border rounded px-3 py-2 text-white font-mono focus:outline-none focus:border-eoc-accent"
              required
            />
          </div>

          {isOverrideMode && overrideDecision ? (
            <>
              <div className="bg-eoc-darkest p-3 rounded border border-slate-800">
                <span className="text-slate-400 block text-[10px] font-mono">TARGET DECISION:</span>
                <span className="text-white font-mono font-bold">
                  {overrideDecision.resource_code} ➔ {overrideDecision.target_zone_name}
                </span>
              </div>

              <div>
                <label className="font-mono font-semibold text-slate-300 block mb-1">
                  Select Override Replacement Resource:
                </label>
                <select
                  value={selectedResourceId}
                  onChange={(e) => setSelectedResourceId(e.target.value)}
                  className="w-full bg-eoc-darkest border border-eoc-border rounded px-3 py-2 text-white font-mono focus:outline-none focus:border-eoc-accent"
                  required
                >
                  <option value="">-- Select Replacement Unit --</option>
                  {resources.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.code} - {r.name} ({r.type})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="font-mono font-semibold text-slate-300 block mb-1">
                  Tactical Override Justification:
                </label>
                <textarea
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  rows={3}
                  className="w-full bg-eoc-darkest border border-eoc-border rounded px-3 py-2 text-white focus:outline-none focus:border-eoc-accent text-xs"
                  required
                />
              </div>
            </>
          ) : (
            <div>
              <label className="font-mono font-semibold text-slate-300 block mb-1">
                Commander Operational Authorization Notes:
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
                className="w-full bg-eoc-darkest border border-eoc-border rounded px-3 py-2 text-white focus:outline-none focus:border-eoc-accent text-xs"
                required
              />
            </div>
          )}

          {/* Footer Buttons */}
          <div className="pt-2 flex items-center justify-end gap-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs font-bold flex items-center gap-2 shadow-glow-success"
            >
              <CheckCircle className="w-4 h-4" />
              <span>{isOverrideMode ? 'Apply Override' : 'Sign & Authorize Dispatch'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
