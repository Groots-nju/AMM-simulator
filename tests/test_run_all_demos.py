from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_run_all_demos_script_executes_all_scenarios_and_exports_comparison(tmp_path: Path) -> None:
    project_dir = Path(__file__).resolve().parents[1]
    output_root = tmp_path / "batch_outputs"

    completed = subprocess.run(
        [sys.executable, "run_all_demos.py", "--output-root", str(output_root)],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=True,
    )

    stdout = completed.stdout
    assert "Running bundled demo scenarios..." in stdout
    assert "Comparison Summary" in stdout
    assert "AMM MVP Demo" in stdout
    assert "AMM Large Trade Shock Demo" in stdout
    assert "AMM IL Stress Demo" in stdout

    scenario_dirs = [
        output_root / "demo",
        output_root / "demo_large_trade_shock",
        output_root / "demo_il_stress",
    ]
    for scenario_dir in scenario_dirs:
        assert scenario_dir.exists()
        assert (scenario_dir / "summary.json").exists()
        assert (scenario_dir / "snapshots.json").exists()
        assert (scenario_dir / "event_records.json").exists()
        assert (scenario_dir / "spot_price_series.png").exists()

    comparison_path = output_root / "demo_comparison.json"
    assert comparison_path.exists()

    comparison_data = json.loads(comparison_path.read_text(encoding="utf-8"))
    assert "scenarios" in comparison_data
    assert len(comparison_data["scenarios"]) == 3
    scenario_names = {row["scenario_name"] for row in comparison_data["scenarios"]}
    assert scenario_names == {
        "AMM MVP Demo",
        "AMM Large Trade Shock Demo",
        "AMM IL Stress Demo",
    }
