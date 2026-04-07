import type { SimulationResponse } from "../lib/api";

type SummaryPanelProps = {
  result: SimulationResponse | null;
};

function displayValue(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }
  return String(value);
}

function formatDecimalValue(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }

  const parsed = typeof value === "number" ? value : Number(value);
  if (Number.isNaN(parsed)) {
    return String(value);
  }

  return parsed.toFixed(6);
}

function formatPercentValue(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }

  const parsed = typeof value === "number" ? value : Number(value);
  if (Number.isNaN(parsed)) {
    return String(value);
  }

  return `${(parsed * 100).toFixed(4)}%`;
}

export function SummaryPanel({ result }: SummaryPanelProps) {
  if (!result) {
    return (
      <section className="panel">
        <h2 className="summary-heading">Simulation Summary</h2>
        <p className="summary-empty">
          Select a demo scenario and run the simulation. The key summary metrics will appear here.
        </p>
      </section>
    );
  }

  const { summary } = result;
  const fields = [
    { label: "Scenario Name", value: summary.scenario_name },
    { label: "Total Events", value: summary.total_events },
    {
      label: "Final Spot Price",
      value: formatDecimalValue(summary.final_spot_price),
    },
    { label: "Latest IL %", value: formatPercentValue(summary.latest_il_pct) },
    { label: "Swap Events", value: summary.swap_event_count },
    { label: "Add Liquidity Events", value: summary.add_liquidity_event_count },
    {
      label: "External Price Updates",
      value: summary.external_price_update_event_count,
    },
  ];

  return (
    <section className="panel">
      <h2 className="summary-heading">Simulation Summary</h2>
      <div className="summary-grid">
        {fields.map((field) => (
          <article className="summary-card" key={field.label}>
            <div className="label">{field.label}</div>
            <div className="value">{displayValue(field.value)}</div>
          </article>
        ))}
      </div>

      <div className="placeholder-panel">
        Plot and event detail panels will be added in the next stage. This page already uses the
        live FastAPI backend response that the chart and detail views will build on.
      </div>
    </section>
  );
}
