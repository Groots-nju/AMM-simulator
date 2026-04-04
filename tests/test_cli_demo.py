from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml


def test_cli_demo_runs_and_generates_chart(tmp_path: Path) -> None:
    project_dir = Path(__file__).resolve().parents[1]
    config_path = project_dir / "data" / "demo.yaml"
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    output_dir = tmp_path / "outputs"
    data["output"]["directory"] = str(output_dir)

    temp_config_path = tmp_path / "demo.yaml"
    temp_config_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "main.py", "--config", str(temp_config_path)],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=True,
    )

    stdout = completed.stdout

    assert "Scenario: AMM MVP Demo" in stdout
    assert "Pool Final State:" in stdout
    assert "spot_price=" in stdout
    assert "LP Positions: 2" in stdout
    assert "Swap #1:" in stdout
    assert "fee=" in stdout
    assert "slippage=" in stdout
    assert "IL Analysis:" in stdout
    assert "Chart saved:" in stdout
    assert "Export saved (summary):" in stdout
    assert "Export saved (snapshots):" in stdout
    assert "Export saved (event_records):" in stdout
    assert output_dir.exists()
    assert (output_dir / "spot_price_series.png").exists()
    assert (output_dir / "lp_vs_hodl.png").exists()
    assert (output_dir / "summary.json").exists()
    assert (output_dir / "snapshots.json").exists()
    assert (output_dir / "event_records.json").exists()

    summary_data = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    snapshots_data = json.loads((output_dir / "snapshots.json").read_text(encoding="utf-8"))
    event_records_data = json.loads((output_dir / "event_records.json").read_text(encoding="utf-8"))

    assert summary_data["total_events"] == 3
    assert summary_data["swap_event_count"] == 1
    assert summary_data["add_liquidity_event_count"] == 1
    assert summary_data["external_price_update_event_count"] == 1
    assert len(snapshots_data) == 4
    assert len(event_records_data) == 3
