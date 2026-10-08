import { EOCState } from './types';

const BASE_URL = import.meta.env.VITE_API_URL || '';

export async function fetchEOCState(): Promise<EOCState> {
  const res = await fetch(`${BASE_URL}/api/state`);
  if (!res.ok) {
    throw new Error(`Failed to fetch EOC state: ${res.statusText}`);
  }
  return res.json();
}

export async function triggerAct2Shock(): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/simulation/act2/shock`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    throw new Error(`Failed to trigger Act 2: ${res.statusText}`);
  }
  return res.json();
}

export async function approvePlan(commanderName: string, notes?: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/simulation/act3/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ commander_name: commanderName, notes }),
  });
  if (!res.ok) {
    throw new Error(`Failed to approve plan: ${res.statusText}`);
  }
  return res.json();
}

export async function resetSimulation(): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/simulation/reset`, {
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error(`Failed to reset simulation: ${res.statusText}`);
  }
  return res.json();
}

export async function overrideDecision(
  decisionId: string,
  newResourceId: string,
  commanderName: string,
  reason: string
): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/plan/override`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      decision_id: decisionId,
      new_resource_id: newResourceId,
      commander_name: commanderName,
      reason,
    }),
  });
  if (!res.ok) {
    throw new Error(`Failed to override decision: ${res.statusText}`);
  }
  return res.json();
}
