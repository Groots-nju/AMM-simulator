"""CLI entrypoint for the minimal AMM simulation MVP."""

from __future__ import annotations

import argparse

from src.decimal_utils import format_decimal, format_percent
from src.models import SimulationResult
from src.pool import Pool
from src.simulation_runner import run_simulation_from_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a minimal AMM exchange simulation demo.")
    parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_output = run_simulation_from_config(args.config)
    print_summary(run_output.pool, run_output.result)


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
