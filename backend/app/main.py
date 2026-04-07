"""FastAPI application entrypoint for the AMM simulator backend."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers.health import router as health_router
from .routers.scenarios import router as scenarios_router
from .routers.simulate import router as simulate_router

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUTS_ROOT = PROJECT_ROOT / "outputs"
OUTPUTS_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="AMM Simulator Backend",
    description="Thin FastAPI wrapper over the existing AMM simulation core.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(scenarios_router)
app.include_router(simulate_router)
app.mount("/artifacts", StaticFiles(directory=OUTPUTS_ROOT), name="artifacts")
