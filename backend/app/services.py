"""Thin backend services that wrap the existing simulation core."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from src.simulation_runner import run_simulation_from_config

from .scenario_registry import ScenarioDefinition, get_scenario_by_id, list_scenarios

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUTS_ROOT = PROJECT_ROOT / "outputs"
WEB_OUTPUTS_ROOT = OUTPUTS_ROOT / "web"


def list_available_scenarios() -> list[dict[str, str]]:
    return [scenario_to_dict(scenario) for scenario in list_scenarios()]


def get_scenario_or_404(scenario_id: str) -> ScenarioDefinition:
    scenario = get_scenario_by_id(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail=f"Unknown scenario_id: {scenario_id}")
    return scenario


def run_scenario_simulation(scenario_id: str) -> dict[str, Any]:
    scenario = get_scenario_or_404(scenario_id)
    config_path = PROJECT_ROOT / scenario.config_path
    scenario_output_dir = WEB_OUTPUTS_ROOT / scenario.id
    run_output = run_simulation_from_config(config_path, output_dir=scenario_output_dir)

    summary = _load_json(run_output.result.export_paths["summary"])
    event_records = _load_json(run_output.result.export_paths["event_records"])

    return {
        "scenario": scenario_to_dict(scenario),
        "summary": summary,
        "plots": [
            {
                "name": Path(plot_path).stem,
                "url": _path_to_artifact_url(plot_path),
            }
            for plot_path in run_output.result.plot_paths
        ],
        "exports": {
            export_name: _path_to_artifact_url(export_path)
            for export_name, export_path in run_output.result.export_paths.items()
        },
        "event_records": [_to_event_record_brief(record) for record in event_records],
    }


def scenario_to_dict(scenario: ScenarioDefinition) -> dict[str, str]:
    return {
        "id": scenario.id,
        "name": scenario.name,
        "description": scenario.description,
        "config_path": scenario.config_path,
    }


def _load_json(path: str | Path) -> Any:
    json_path = Path(path)
    with json_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _path_to_artifact_url(path: str | Path) -> str:
    artifact_path = Path(path).resolve()
    relative_path = artifact_path.relative_to(OUTPUTS_ROOT.resolve())
    return f"/artifacts/{relative_path.as_posix()}"


def _to_event_record_brief(record: dict[str, Any]) -> dict[str, Any]:
    swap_result = record.get("swap_result")
    il_analysis = record.get("il_analysis")
    return {
        "step": record["step"],
        "timestamp": record["timestamp"],
        "event_type": record["event_type"],
        "actor": record["actor"],
        "amount_in": swap_result["amount_in"] if swap_result else None,
        "amount_out": swap_result["amount_out"] if swap_result else None,
        "slippage": swap_result["slippage"] if swap_result else None,
        "il_pct": il_analysis["impermanent_loss_pct"] if il_analysis else None,
    }
