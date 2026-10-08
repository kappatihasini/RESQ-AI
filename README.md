# RESQ-AI: Adaptive Emergency Decision & Resource Replanning Engine

> **Domain:** Smart Automation / Disaster Resource Coordination  
> **Target:** National-Level Hackathon Demonstration  
> **Designation:** AI-Assisted Decision Support System (Simulation Environment)

---

## 🌟 Overview
**RESQ-AI** is a closed-loop, deterministic decision-support and replanning engine that converts noisy, conflicting emergency data into explainable, prioritized resource-allocation decisions and automatically re-optimizes when disaster conditions shift.

### The Four Core Engines
1. **Multi-Source Intelligence Engine (`MultiSourceEngine`):** Spatio-temporal deduplication, conflict detection (road status contradictions, casualty count discrepancies, water depth variances), and mathematical evidence confidence scoring ($C_{ev}$).
2. **Critical-Zone Intelligence Engine (`CriticalZoneEngine`):** Geographic incident clustering and explainable priority scoring ($0 - 100$) combining Urgency, Severity, Vulnerability, Accessibility friction, and Verified Confidence.
3. **Resource Allocation Engine (`ResourceAllocatorEngine`):** Deterministic bipartite matching under capability constraints, route viability, and capacity limits with full decision traces ("Why this unit?", "Alternative rejected").
4. **Dynamic Replanning Engine (`DynamicReplanningEngine`):** Automated event-triggered re-optimization producing instant **"Old Plan vs New Plan"** differential comparison matrices.

---

## 🌐 Live Cloud Deployment
* **Production Command Center:** [https://resq-ai-red.vercel.app](https://resq-ai-red.vercel.app)
* **Live API Health Check:** [https://resq-ai-red.vercel.app/api/health](https://resq-ai-red.vercel.app/api/health)
* **Live Synchronized State API:** [https://resq-ai-red.vercel.app/api/state](https://resq-ai-red.vercel.app/api/state)

---

## 🚀 Quick Start Instructions

### 1. Start the Backend API (FastAPI)
```powershell
cd resq-ai/backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
* Interactive API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Health Status: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### 2. Start the Frontend (React + Vite + Tailwind)
```powershell
cd resq-ai/frontend
npm run dev
```
* Tactical EOC Command Center: [http://localhost:5173](http://localhost:5173)

---

## 🎯 3-Act Jury Demonstration Walkthrough

1. **Act I: Multi-Source Evidence Influx**
   - Ingests noisy reports across Citizen SOS, Field Drones, and IoT River Gauges.
   - Highlights duplicate clustering and flags contradictory road reports.
   - Shows ranked Critical Zones (Zone Alpha Hospital at P1 with 98.1 score).
   - Formulates Initial Allocation Plan v1 with full decision explanations.
2. **Act II: Shock Event & Dynamic Replanning**
   - Click **"Inject Act II Shock Event"**.
   - Simulates Bhatia Bridge collapse and flash surge into Industrial Chemical Corridor.
   - Dynamic Replanner triggers in $< 35\text{ms}$.
   - Shows **Old Plan vs New Plan Diff**, diverting rescue boats and ambulances to the highest life-threat crisis.
3. **Act III: Human Commander Authorization & Dispatch**
   - Click **"Review & Authorize Replan"**.
   - Commander V. Sharma reviews ethical and mathematical trade-offs and officially authorizes dispatch.
   - Units transition to `EN_ROUTE` with live telemetry tracking vectors on the Leaflet Tactical Map.
