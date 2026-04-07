"""Pydantic schemas for the FastAPI backend."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class ScenarioItem(BaseModel):
    id: str
    name: str
    description: str
    config_path: str


class SimulateRequest(BaseModel):
    scenario_id: str


class ArtifactLink(BaseModel):
    name: str
    url: str


class EventRecordBrief(BaseModel):
    step: int
    timestamp: int
    event_type: str
    actor: str
    amount_in: str | None = None
    amount_out: str | None = None
    slippage: str | None = None
    il_pct: str | None = None


class SimulateResponse(BaseModel):
    scenario: ScenarioItem
    summary: dict[str, Any]
    plots: list[ArtifactLink]
    exports: dict[str, str]
    event_records: list[EventRecordBrief]
