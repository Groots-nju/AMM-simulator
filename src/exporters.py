"""JSON exporters for simulation results."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from .models import SimulationResult


def export_simulation_result(result: SimulationResult, output_dir: str | Path) -> dict[str, str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    summary_path = output_path / "summary.json"
    snapshots_path = output_path / "snapshots.json"
    event_records_path = output_path / "event_records.json"

    _write_json(summary_path, result.summary)
    _write_json(snapshots_path, result.snapshots)
    _write_json(event_records_path, result.event_records)

    return {
        "summary": str(summary_path),
        "snapshots": str(snapshots_path),
        "event_records": str(event_records_path),
    }


def _write_json(path: Path, payload: Any) -> None:
    serializable = _to_serializable(payload)
    with path.open("w", encoding="utf-8") as file:
        json.dump(serializable, file, indent=2, ensure_ascii=False, sort_keys=True)


def _to_serializable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if is_dataclass(value):
        return _to_serializable(asdict(value))
    if isinstance(value, dict):
        return {str(key): _to_serializable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_serializable(item) for item in value]
    if isinstance(value, tuple):
        return [_to_serializable(item) for item in value]
    return value
