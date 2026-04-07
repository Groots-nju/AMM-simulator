import type { EventRecordBrief, SimulationResponse } from "../lib/api";

type EventRecordsPanelProps = {
  result: SimulationResponse | null;
};

function formatValue(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }
  return String(value);
}

function formatDecimal(value: string | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }

  const parsed = Number(value);
  if (Number.isNaN(parsed)) {
    return value;
  }

  return parsed.toFixed(6);
}

function formatPercent(value: string | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }

  const parsed = Number(value);
  if (Number.isNaN(parsed)) {
    return value;
  }

  return `${(parsed * 100).toFixed(4)}%`;
}

export function EventRecordsPanel({ result }: EventRecordsPanelProps) {
  if (!result) {
    return (
      <section className="panel">
        <h2 className="summary-heading">Event Records</h2>
        <p className="summary-empty">
          Run a scenario to inspect the step-by-step event records returned by the backend.
        </p>
      </section>
    );
  }

  if (result.event_records.length === 0) {
    return (
      <section className="panel">
        <h2 className="summary-heading">Event Records</h2>
        <p className="summary-empty">No event records are available for this scenario.</p>
      </section>
    );
  }

  return (
    <section className="panel">
      <h2 className="summary-heading">Event Records</h2>
      <div className="records-table-wrapper">
        <table className="records-table">
          <thead>
            <tr>
              <th>Step</th>
              <th>Event Type</th>
              <th>Actor</th>
              <th>Amount In</th>
              <th>Amount Out</th>
              <th>Slippage</th>
              <th>IL %</th>
            </tr>
          </thead>
          <tbody>
            {result.event_records.map((record: EventRecordBrief) => (
              <tr key={`${record.step}-${record.event_type}-${record.actor}`}>
                <td>{formatValue(record.step)}</td>
                <td>{formatValue(record.event_type)}</td>
                <td>{formatValue(record.actor)}</td>
                <td>{formatDecimal(record.amount_in)}</td>
                <td>{formatDecimal(record.amount_out)}</td>
                <td>{formatPercent(record.slippage)}</td>
                <td>{formatPercent(record.il_pct)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
