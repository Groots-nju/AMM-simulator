from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_scenarios_endpoint_returns_three_built_in_scenarios() -> None:
    response = client.get("/scenarios")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 3
    assert {item["id"] for item in payload} == {"baseline", "large-trade-shock", "il-stress"}


def test_simulate_endpoint_runs_baseline_scenario() -> None:
    response = client.post("/simulate", json={"scenario_id": "baseline"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["scenario"]["id"] == "baseline"
    assert payload["summary"]["scenario_name"] == "AMM MVP Demo"
    assert payload["summary"]["total_events"] == 3
    assert payload["summary"]["swap_event_count"] == 1
    assert payload["summary"]["add_liquidity_event_count"] == 1
    assert payload["summary"]["external_price_update_event_count"] == 1
    assert payload["plots"]
    assert payload["plots"][0]["url"].startswith("/artifacts/web/baseline/")
    assert payload["exports"]["summary"].startswith("/artifacts/web/baseline/")
    assert len(payload["event_records"]) == 3
