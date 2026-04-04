"""CLI entrypoint for the minimal AMM simulation MVP."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.config import load_config
from src.decimal_utils import format_decimal, format_percent
from src.exporters import export_simulation_result
from src.models import SimulationResult
from src.pool import Pool
from src.reporting import build_summary
from src.visualization import save_visualizations
from simulator.engine import SimulationEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a minimal AMM exchange simulation demo.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

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

    output_dir = Path(config["output"]["directory"])
    if config["visualization"]["enabled"] and config["output"]["save_plots"]:
        result.plot_paths.extend(save_visualizations(result, output_dir))

    result.summary = build_summary(pool, result)
    result.export_paths = export_simulation_result(result, output_dir)
    print_summary(pool, result)


def print_summary(pool: Pool, result: SimulationResult) -> None:
    print(f"Scenario: {result.scenario_name}")
    print(
        "Pool Final State: "
        f"{pool.token0.symbol}={format_decimal(pool.reserve0)}, "
        f"{pool.token1.symbol}={format_decimal(pool.reserve1)}, "
        f"spot_price={format_decimal(pool.spot_price_token1_per_token0())} {pool.token1.symbol}/{pool.token0.symbol}"
    )
    print(f"LP Positions: {len(result.lp_positions)}")

    for index, swap_result in enumerate(result.swap_results, start=1):
        print(
            f"Swap #{index}: actor={swap_result.actor}, "
            f"{swap_result.amount_in} {swap_result.token_in_symbol} -> "
            f"{format_decimal(swap_result.amount_out)} {swap_result.token_out_symbol}, "
            f"fee={format_decimal(swap_result.fee_amount)}, "
            f"slippage={format_percent(swap_result.slippage)}"
        )

    if result.il_analysis is not None:
        analysis = result.il_analysis
        print(
            "IL Analysis: "
            f"owner={analysis.owner_id}, "
            f"external_price={format_decimal(analysis.external_price_token1_per_token0)}, "
            f"lp_value={format_decimal(analysis.lp_value_in_token1)} {pool.token1.symbol}, "
            f"hodl_value={format_decimal(analysis.hodl_value_in_token1)} {pool.token1.symbol}, "
            f"IL={format_percent(analysis.impermanent_loss_pct)}"
        )

    for plot_path in result.plot_paths:
        print(f"Chart saved: {plot_path}")

    for export_name, export_path in sorted(result.export_paths.items()):
        print(f"Export saved ({export_name}): {export_path}")


if __name__ == "__main__":
    main()
