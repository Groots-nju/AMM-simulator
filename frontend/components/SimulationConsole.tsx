"use client";

import { useMemo, useState } from "react";

import type { ScenarioItem, SimulationResponse } from "../lib/api";
import { simulateScenario } from "../lib/api";
import { RunButton } from "./RunButton";
import { ScenarioSelector } from "./ScenarioSelector";
import { SummaryPanel } from "./SummaryPanel";

type SimulationConsoleProps = {
  initialScenarios: ScenarioItem[];
  initialError?: string | null;
};

export function SimulationConsole({
  initialScenarios,
  initialError = null,
}: SimulationConsoleProps) {
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>(initialScenarios[0]?.id ?? "");
  const [result, setResult] = useState<SimulationResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(initialError);

  const selectedScenario = useMemo(
    () => initialScenarios.find((scenario) => scenario.id === selectedScenarioId) ?? null,
    [initialScenarios, selectedScenarioId],
  );

  async function handleRunSimulation() {
    if (!selectedScenarioId) {
      setError("Please select a scenario first.");
      return;
    }

    setIsRunning(true);
    setError(null);

    try {
      const response = await simulateScenario(selectedScenarioId);
      setResult(response);
    } catch (runError) {
      const message =
        runError instanceof Error ? runError.message : "Failed to run the simulation.";
      setError(message);
      setResult(null);
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <div className="stack">
      <section className="panel stack">
        <div className="control-row">
          <ScenarioSelector
            scenarios={initialScenarios}
            value={selectedScenarioId}
            disabled={initialScenarios.length === 0 || isRunning}
            onChange={setSelectedScenarioId}
          />
          {selectedScenario ? (
            <div className="scenario-meta">
              <strong>{selectedScenario.name}</strong>
              <br />
              {selectedScenario.description}
            </div>
          ) : (
            <div className="scenario-meta">No scenario is available right now.</div>
          )}
        </div>
        <RunButton
          disabled={initialScenarios.length === 0}
          loading={isRunning}
          onClick={handleRunSimulation}
        />
      </section>

      {isRunning ? <div className="status loading">Running simulation...</div> : null}
      {error ? <div className="status error">{error}</div> : null}
      {result && !error ? <div className="status success">Simulation completed successfully.</div> : null}

      <SummaryPanel result={result} />
    </div>
  );
}
