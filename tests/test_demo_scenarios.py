from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


def run_demo_with_temp_output(project_dir: Path, config_name: str, tmp_path: Path) -> tuple[subprocess.CompletedProcess[str], Path]:
    config_path = project_dir / "data" / config_name
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    output_dir = tmp_path / config_name.replace(".yaml", "")
    data["output"]["directory"] = str(output_dir)

    temp_config_path = tmp_path / config_name
    temp_config_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "main.py", "--config", str(temp_config_path)],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    return completed, output_dir


@pytest.mark.parametrize(
    ("config_name", "expected_total_events"),
    [
        ("demo_large_trade_shock.yaml", 1),
        ("demo_il_stress.yaml", 2),
    ],
)
def test_additional_demo_scenarios_run_and_export_outputs(
    tmp_path: Path,
    config_name: str,
    expected_total_events: int,
) -> None:
    project_dir = Path(__file__).resolve().parents[1]
    completed, output_dir = run_demo_with_temp_output(project_dir, config_name, tmp_path)

    assert "Scenario:" in completed.stdout
    assert "Pool Final State:" in completed.stdout
    assert "Export saved (summary):" in completed.stdout
    assert (output_dir / "spot_price_series.png").exists()
    assert (output_dir / "summary.json").exists()
    assert (output_dir / "snapshots.json").exists()
    assert (output_dir / "event_records.json").exists()

    summary_data = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    snapshots_data = json.loads((output_dir / "snapshots.json").read_text(encoding="utf-8"))
    event_records_data = json.loads((output_dir / "event_records.json").read_text(encoding="utf-8"))

    assert summary_data["total_events"] == expected_total_events
    assert len(snapshots_data) == expected_total_events + 1
    assert len(event_records_data) == expected_total_events


def test_large_trade_shock_scenario_exhibits_severe_negative_slippage(tmp_path: Path) -> None:
    project_dir = Path(__file__).resolve().parents[1]
    completed, output_dir = run_demo_with_temp_output(project_dir, "demo_large_trade_shock.yaml", tmp_path)

    event_records_data = json.loads((output_dir / "event_records.json").read_text(encoding="utf-8"))
    summary_data = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))

    assert "Swap #1:" in completed.stdout
    assert summary_data["swap_event_count"] == 1
    assert summary_data["latest_il_pct"] is None
    assert float(event_records_data[0]["swap_result"]["slippage"]) < -0.2
    assert float(summary_data["final_spot_price"]) < 1000


def test_il_stress_scenario_exhibits_more_visible_il_and_lp_chart(tmp_path: Path) -> None:
    project_dir = Path(__file__).resolve().parents[1]
    completed, output_dir = run_demo_with_temp_output(project_dir, "demo_il_stress.yaml", tmp_path)

    summary_data = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))

    assert "IL Analysis:" in completed.stdout
    assert summary_data["add_liquidity_event_count"] == 1
    assert summary_data["external_price_update_event_count"] == 1
    assert float(summary_data["latest_il_pct"]) < -0.05
    assert (output_dir / "lp_vs_hodl.png").exists()
