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

export function SummaryPanel({ result }: SummaryPanelProps) {
  if (!result) {
    return null;
  }

  const { summary } = result;
  const fields = [
    { label: "Scenario Name", value: summary.scenario_name },
    { label: "Total Events", value: summary.total_events },
    { label: "Final Spot Price", value: summary.final_spot_price },
    { label: "Latest IL %", value: summary.latest_il_pct },
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
    </section>
  );
}
