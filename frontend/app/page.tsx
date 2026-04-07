import { SimulationConsole } from "../components/SimulationConsole";
import { getScenarios, type ScenarioItem } from "../lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  let initialError: string | null = null;
  let scenarios: ScenarioItem[] = [];

  try {
    scenarios = await getScenarios();
  } catch (error) {
    initialError =
      error instanceof Error
        ? error.message
        : "Failed to load scenarios from the backend service.";
  }

  return (
    <main className="page-shell">
      <header className="hero">
        <h1>AMM Simulator Web</h1>
        <p>
          A minimal web UI that reuses the existing Python AMM simulation core.
          Select one of the built-in demo scenarios, run it against the FastAPI backend,
          and inspect the key summary metrics returned by the simulator.
        </p>
      </header>

      <SimulationConsole initialScenarios={scenarios} initialError={initialError} />
    </main>
  );
}
