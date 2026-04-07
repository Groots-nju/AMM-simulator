"""Scenario listing API."""

from __future__ import annotations

from fastapi import APIRouter

from ..schemas import ScenarioItem
from ..services import list_available_scenarios

router = APIRouter(tags=["scenarios"])


@router.get("/scenarios", response_model=list[ScenarioItem])
def get_scenarios() -> list[ScenarioItem]:
    return [ScenarioItem(**scenario) for scenario in list_available_scenarios()]
