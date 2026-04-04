"""Visualization helpers that only read simulation outputs."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

_mpl_cache = Path(tempfile.gettempdir()) / "amm_mpl_cache"
_xdg_cache = Path(tempfile.gettempdir()) / "amm_xdg_cache"
_mpl_cache.mkdir(parents=True, exist_ok=True)
_xdg_cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_mpl_cache))
os.environ.setdefault("XDG_CACHE_HOME", str(_xdg_cache))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from .models import SimulationResult


def save_visualizations(result: SimulationResult, output_dir: str | Path) -> list[str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    plot_paths = [save_spot_price_series_plot(result, output_path)]
    if result.il_analysis is not None:
        plot_paths.append(save_lp_vs_hodl_plot(result, output_path))
    return plot_paths


def save_spot_price_series_plot(result: SimulationResult, output_dir: str | Path) -> str:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    steps = [snapshot.step for snapshot in result.snapshots]
    prices = [float(snapshot.spot_price_token1_per_token0) for snapshot in result.snapshots]

    figure, axis = plt.subplots(figsize=(10, 4.5), constrained_layout=True)
    axis.plot(steps, prices, marker="o", color="#1f77b4", linewidth=2)
    axis.set_title("Spot Price by Simulation Step")
    axis.set_xlabel("Step")
    axis.set_ylabel("Price (token1 per token0)")
    axis.grid(True, alpha=0.3)
    axis.set_xticks(steps)

    chart_path = output_path / "spot_price_series.png"
    figure.savefig(chart_path, dpi=150)
    plt.close(figure)
    return str(chart_path)


def save_lp_vs_hodl_plot(result: SimulationResult, output_dir: str | Path) -> str:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    if result.il_analysis is None:
        raise ValueError("LP vs HODL plot requires IL analysis data.")

    labels = ["LP Value", "HODL Value"]
    values = [
        float(result.il_analysis.lp_value_in_token1),
        float(result.il_analysis.hodl_value_in_token1),
    ]

    figure, axis = plt.subplots(figsize=(8, 5), constrained_layout=True)
    bars = axis.bar(labels, values, color=["#2ca02c", "#ff7f0e"], width=0.55)
    axis.set_title("LP Value vs HODL Value")
    axis.set_xlabel("Portfolio")
    axis.set_ylabel("Value (in token1)")
    axis.grid(True, axis="y", alpha=0.3)

    il_pct = float(result.il_analysis.impermanent_loss_pct * 100)
    axis.text(
        0.5,
        max(values) * 0.97 if max(values) > 0 else 0,
        f"Latest IL: {il_pct:.4f}%",
        ha="center",
        va="top",
        fontsize=10,
    )

    for bar, value in zip(bars, values):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    chart_path = output_path / "lp_vs_hodl.png"
    figure.savefig(chart_path, dpi=150)
    plt.close(figure)
    return str(chart_path)
