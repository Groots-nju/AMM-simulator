import type { ScenarioItem } from "../lib/api";

type ScenarioSelectorProps = {
  scenarios: ScenarioItem[];
  value: string;
  disabled?: boolean;
  onChange: (value: string) => void;
};

export function ScenarioSelector({
  scenarios,
  value,
  disabled = false,
  onChange,
}: ScenarioSelectorProps) {
  return (
    <div>
      <label className="field-label" htmlFor="scenario-select">
        Demo Scenario
      </label>
      <select
        id="scenario-select"
        className="select"
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      >
        {scenarios.map((scenario) => (
          <option key={scenario.id} value={scenario.id}>
            {scenario.name}
          </option>
        ))}
      </select>
    </div>
  );
}
