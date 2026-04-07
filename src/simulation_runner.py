"""Shared simulation runner used by CLI and web layers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from simulator.engine import SimulationEngine

from .config import load_config
from .exporters import export_simulation_result
from .models import SimulationResult
from .pool import Pool
from .reporting import build_summary
from .visualization import save_visualizations


@dataclass
class SimulationRunOutput:
    config: dict[str, Any]
    pool: Pool
    result: SimulationResult
    output_dir: Path


def run_simulation_from_config(
    config_path: str | Path,
    *,
    output_dir: str | Path | None = None,
    save_plots: bool | None = None,
    export_results: bool = True,
) -> SimulationRunOutput:
    """Run one simulation scenario from a config file."""
    config = load_config(config_path)
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

    resolved_output_dir = Path(output_dir) if output_dir is not None else Path(config["output"]["directory"])
    should_save_plots = (
        config["visualization"]["enabled"] and config["output"]["save_plots"]
        if save_plots is None
        else save_plots
    )

    if should_save_plots:
        result.plot_paths.extend(save_visualizations(result, resolved_output_dir))

    result.summary = build_summary(pool, result)
    if export_results:
        result.export_paths = export_simulation_result(result, resolved_output_dir)

    return SimulationRunOutput(
        config=config,
        pool=pool,
        result=result,
        output_dir=resolved_output_dir,
    )
