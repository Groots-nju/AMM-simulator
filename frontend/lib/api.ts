export type ScenarioItem = {
  id: string;
  name: string;
  description: string;
  config_path: string;
};

export type SimulationSummary = {
  scenario_name?: string;
  total_events?: number;
  final_spot_price?: string;
  latest_il_pct?: string | null;
  swap_event_count?: number;
  add_liquidity_event_count?: number;
  external_price_update_event_count?: number;
};

export type SimulationResponse = {
  scenario: ScenarioItem;
  summary: SimulationSummary;
  plots: Array<{ name: string; url: string }>;
  exports: Record<string, string>;
  event_records: Array<{
    step: number;
    timestamp: number;
    event_type: string;
    actor: string;
    amount_in?: string | null;
    amount_out?: string | null;
    slippage?: string | null;
    il_pct?: string | null;
  }>;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

async function parseJsonOrThrow<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        detail = payload.detail;
      }
    } catch {
      // Ignore JSON parse failures and keep the fallback detail.
    }
    throw new Error(detail);
  }
  return (await response.json()) as T;
}

export async function getScenarios(): Promise<ScenarioItem[]> {
  const response = await fetch(`${API_BASE_URL}/scenarios`, {
    cache: "no-store",
  });
  return parseJsonOrThrow<ScenarioItem[]>(response);
}

export async function simulateScenario(scenarioId: string): Promise<SimulationResponse> {
  const response = await fetch(`${API_BASE_URL}/simulate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ scenario_id: scenarioId }),
    cache: "no-store",
  });
  return parseJsonOrThrow<SimulationResponse>(response);
}
