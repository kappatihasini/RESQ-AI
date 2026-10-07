import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api():
    print("Testing RESQ-AI FastAPI Endpoints...")

    # Root
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["engine"] == "RESQ-AI"
    print("[PASS] Root health check OK")

    # State
    res = client.get("/api/state")
    assert res.status_code == 200
    state = res.json()
    assert state["current_act"] == 1
    assert len(state["zones"]) >= 4
    assert len(state["resources"]) >= 8
    print(f"[PASS] GET /api/state OK (Act {state['current_act']}, Zones: {len(state['zones'])})")

    # Incidents
    res = client.get("/api/incidents")
    assert res.status_code == 200
    incidents = res.json()
    assert len(incidents) >= 1
    print(f"[PASS] GET /api/incidents OK ({len(incidents)} verified incidents)")

    # Zones
    res = client.get("/api/zones")
    assert res.status_code == 200
    zones = res.json()
    assert len(zones) >= 4
    print(f"[PASS] GET /api/zones OK (Top Zone: {zones[0]['name']} - Priority: {zones[0]['priority_score']})")

    # Current Plan
    res = client.get("/api/plan")
    assert res.status_code == 200
    plan = res.json()
    assert plan["plan_version"] == 1
    assert len(plan["decisions"]) >= 3
    print(f"[PASS] GET /api/plan OK (Plan v{plan['plan_version']}, Decisions: {len(plan['decisions'])})")

    # Act 2 Shock Trigger
    print("Triggering Act 2 Shock Event via API...")
    res = client.post("/api/simulation/act2/shock")
    assert res.status_code == 200
    act2_data = res.json()
    assert act2_data["act"] == 2
    assert act2_data["diff"]["diverted_count"] >= 1
    print(f"[PASS] POST /api/simulation/act2/shock OK (Diverted: {act2_data['diff']['diverted_count']} units)")

    # Plan Diff
    res = client.get("/api/plan/diff")
    assert res.status_code == 200
    diff_data = res.json()
    assert diff_data["diff_available"] is True
    print(f"[PASS] GET /api/plan/diff OK (Summary: {diff_data['diff']['executive_diff_summary']})")

    # Act 3 Approval Trigger
    print("Triggering Act 3 Approval via API...")
    res = client.post("/api/simulation/act3/approve", json={"commander_name": "Commander V. Sharma", "notes": "Authorized"})
    assert res.status_code == 200
    act3_data = res.json()
    assert act3_data["status"] == "APPROVED"
    print("[PASS] POST /api/simulation/act3/approve OK (Plan Officially Approved)")

    # Reset
    res = client.post("/api/simulation/reset")
    assert res.status_code == 200
    print("[PASS] POST /api/simulation/reset OK (Back to Act 1)")

    print("\n=======================================================")
    print("ALL API ENDPOINTS VALIDATED AND RESPONDING 100% OK!")
    print("=======================================================\n")


if __name__ == "__main__":
    test_api()
