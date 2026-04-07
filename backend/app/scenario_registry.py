"""Static registry of built-in demo scenarios."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioDefinition:
    id: str
    name: str
    description: str
    config_path: str


SCENARIOS: list[ScenarioDefinition] = [
    ScenarioDefinition(
        id="baseline",
        name="Baseline Demo",
        description="普通 swap + add_liquidity + external price update。",
        config_path="data/demo.yaml",
    ),
    ScenarioDefinition(
        id="large-trade-shock",
        name="Large Trade Shock",
        description="展示大额交易造成的价格冲击和滑点恶化。",
        config_path="data/demo_large_trade_shock.yaml",
    ),
    ScenarioDefinition(
        id="il-stress",
        name="IL Stress",
        description="展示外部价格剧烈变化下更明显的无常损失。",
        config_path="data/demo_il_stress.yaml",
    ),
]


def list_scenarios() -> list[ScenarioDefinition]:
    return SCENARIOS


def get_scenario_by_id(scenario_id: str) -> ScenarioDefinition | None:
    return next((scenario for scenario in SCENARIOS if scenario.id == scenario_id), None)
