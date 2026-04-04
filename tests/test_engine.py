from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulator.engine import SimulationEngine
from src.config import load_config
from src.pool import Pool
from src.reporting import build_summary


def test_engine_executes_demo_events_in_order_and_records_results() -> None:
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

    assert len(result.event_records) == len(config["events"])
    assert len(result.snapshots) == len(config["events"]) + 1
    assert [record.event_type for record in result.event_records] == [
        "swap",
        "add_liquidity",
        "external_price_update",
    ]
    assert result.event_records[0].swap_result is not None
    assert result.event_records[1].minted_position is not None
    assert result.event_records[1].minted_position.shares > Decimal("0")
    assert result.event_records[2].il_analysis is not None
    assert result.il_analysis is not None
    assert pool.reserve0 == Decimal("130")

    swap_amount_in = config["events"][0].payload["amount_in"]
    effective_in = swap_amount_in * (Decimal("1") - pool_cfg["fee_rate"])
    expected_swap_out = pool_cfg["initial_reserve1"] * effective_in / (
        pool_cfg["initial_reserve0"] + effective_in
    )
    expected_final_reserve1 = (
        pool_cfg["initial_reserve1"]
        - expected_swap_out
        + config["events"][1].payload["amount1"]
    )
    assert pool.reserve1 == expected_final_reserve1

    summary = build_summary(pool, result)
    assert summary["total_events"] == 3
    assert summary["swap_event_count"] == 1
    assert summary["add_liquidity_event_count"] == 1
    assert summary["external_price_update_event_count"] == 1
    assert summary["final_reserve0"] == pool.reserve0
    assert summary["final_reserve1"] == pool.reserve1
    assert summary["total_fees_collected"]["ETH"] == Decimal("0.030")
    assert summary["latest_lp_value"] is not None
    assert summary["latest_hodl_value"] is not None
    assert summary["latest_il_pct"] is not None
