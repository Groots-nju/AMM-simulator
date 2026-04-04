"""Run all bundled demo scenarios and print a compact comparison summary."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

DEMO_CONFIGS = [
    Path("data/demo.yaml"),
    Path("data/demo_large_trade_shock.yaml"),
    Path("data/demo_il_stress.yaml"),
]

COMPARISON_FIELDS = [
    "scenario_name",
    "total_events",
    "final_spot_price",
    "swap_event_count",
    "add_liquidity_event_count",
    "external_price_update_event_count",
    "latest_il_pct",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run all built-in AMM demo scenarios.")
    parser.add_argument(
        "--output-root",
        help="Optional root directory for batch outputs. Each scenario will use a subdirectory under this path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parent
    output_root = Path(args.output_root).resolve() if args.output_root else (project_root / "outputs")
    output_root.mkdir(parents=True, exist_ok=True)

    print("Running bundled demo scenarios...\n")

    comparison_rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="amm_demo_batch_") as temp_dir:
        temp_dir_path = Path(temp_dir)
        for index, config_rel_path in enumerate(DEMO_CONFIGS, start=1):
            scenario_result = run_single_demo(
                project_root=project_root,
                config_rel_path=config_rel_path,
                output_root=output_root,
                temp_dir=temp_dir_path,
            )
            comparison_rows.append(scenario_result["comparison_row"])
            print(
                f"[{index}/{len(DEMO_CONFIGS)}] {scenario_result['comparison_row']['scenario_name']} "
                f"-> {scenario_result['output_dir']}"
            )

    comparison_payload = {"scenarios": comparison_rows}
    comparison_path = output_root / "demo_comparison.json"
    comparison_path.write_text(
        json.dumps(comparison_payload, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )

    print("\nComparison Summary")
    print(render_table(comparison_rows))
    print(f"\nComparison file saved: {comparison_path}")


def run_single_demo(
    *,
    project_root: Path,
    config_rel_path: Path,
    output_root: Path,
    temp_dir: Path,
) -> dict[str, Any]:
    config_path = project_root / config_rel_path
    output_dir = output_root / config_path.stem
    temporary_config_path = build_temp_config(
        original_config_path=config_path,
        temporary_config_path=temp_dir / config_path.name,
        output_dir=output_dir,
    )

    subprocess.run(
        [sys.executable, "main.py", "--config", str(temporary_config_path)],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
    )

    summary_path = output_dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    comparison_row = {field: summary.get(field) for field in COMPARISON_FIELDS}
    comparison_row["config_name"] = config_path.name
    return {
        "output_dir": output_dir,
        "summary": summary,
        "comparison_row": comparison_row,
    }


def build_temp_config(
    *,
    original_config_path: Path,
    temporary_config_path: Path,
    output_dir: Path,
) -> Path:
    config_data = yaml.safe_load(original_config_path.read_text(encoding="utf-8"))
    config_data["output"]["directory"] = str(output_dir)
    temporary_config_path.write_text(yaml.safe_dump(config_data, sort_keys=False), encoding="utf-8")
    return temporary_config_path


def render_table(rows: list[dict[str, Any]]) -> str:
    display_rows = [{field: stringify(row.get(field)) for field in COMPARISON_FIELDS} for row in rows]
    widths = {
        field: max(len(field), *(len(row[field]) for row in display_rows))
        for field in COMPARISON_FIELDS
    }

    header = " | ".join(field.ljust(widths[field]) for field in COMPARISON_FIELDS)
    separator = "-+-".join("-" * widths[field] for field in COMPARISON_FIELDS)
    body = [
        " | ".join(row[field].ljust(widths[field]) for field in COMPARISON_FIELDS)
        for row in display_rows
    ]
    return "\n".join([header, separator, *body])


def stringify(value: Any) -> str:
    if value is None:
        return "-"
    return str(value)


if __name__ == "__main__":
    main()
