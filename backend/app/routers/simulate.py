"""Simulation execution API."""

from __future__ import annotations

from fastapi import APIRouter

from ..schemas import ArtifactLink, EventRecordBrief, SimulateRequest, SimulateResponse
from ..services import run_scenario_simulation

router = APIRouter(tags=["simulate"])


@router.post("/simulate", response_model=SimulateResponse)
def simulate(request: SimulateRequest) -> SimulateResponse:
    payload = run_scenario_simulation(request.scenario_id)
    return SimulateResponse(
        scenario=payload["scenario"],
        summary=payload["summary"],
        plots=[ArtifactLink(**plot) for plot in payload["plots"]],
        exports=payload["exports"],
        event_records=[EventRecordBrief(**record) for record in payload["event_records"]],
    )
