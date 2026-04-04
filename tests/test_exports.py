from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulator.engine import SimulationEngine
from src.config import load_config
from src.exporters import export_simulation_result
from src.pool import Pool
from src.reporting import build_summary


def test_exported_json_matches_result_structure(tmp_path: Path) -> None:
    project_dir = Path(__file__).resolve().parents[1]
    config = load_config(project_dir / "data" / "demo.yaml")
    pool_cfg = config["pool"]
    pool = Pool(
        token0=config["tokens"]["token0"],
        token1=config["tokens"]["token1"],
        fee_rate=pool_cfg["fee_rate"],
    )
    engine = SimulationEngine(
        pool=pool,
        scenario_name=config["project_name"],
        initial_lp_owner=pool_cfg["initial_lp_owner"],
        initial_reserve0=pool_cfg["initial_reserve0"],
        initial_reserve1=pool_cfg["initial_reserve1"],
    )
    result = engine.run(config["events"])
    result.summary = build_summary(pool, result)

    export_paths = export_simulation_result(result, tmp_path)

    summary_data = json.loads(Path(export_paths["summary"]).read_text(encoding="utf-8"))
    snapshots_data = json.loads(Path(export_paths["snapshots"]).read_text(encoding="utf-8"))
    event_records_data = json.loads(Path(export_paths["event_records"]).read_text(encoding="utf-8"))

    assert set(export_paths) == {"summary", "snapshots", "event_records"}
    assert summary_data["scenario_name"] == "AMM MVP Demo"
    assert summary_data["total_events"] == len(result.event_records)
    assert summary_data["final_reserve0"] == "130"
    assert summary_data["final_lp_ownership_by_owner"]["genesis_lp"] == str(
        result.lp_positions["genesis_lp"].shares / pool.total_lp_shares
    )
    assert summary_data["total_fees_collected"]["ETH"] == "0.030"
    assert len(snapshots_data) == len(result.snapshots)
    assert snapshots_data[-1]["reserve1"] == str(pool.reserve1)
    assert len(event_records_data) == len(result.event_records)
    assert event_records_data[0]["event_type"] == "swap"
    assert event_records_data[0]["swap_result"]["fee_amount"] == "0.030"
    assert event_records_data[1]["minted_position"]["shares"] == str(
        result.event_records[1].minted_position.shares
    )
    assert event_records_data[2]["il_analysis"]["impermanent_loss_pct"] == str(
        result.il_analysis.impermanent_loss_pct
    )
