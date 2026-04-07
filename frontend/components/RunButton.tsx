type RunButtonProps = {
  disabled?: boolean;
  loading?: boolean;
  onClick: () => void;
};

export function RunButton({ disabled = false, loading = false, onClick }: RunButtonProps) {
  return (
    <button className="button" type="button" disabled={disabled || loading} onClick={onClick}>
      {loading ? "Running..." : "Run Simulation"}
    </button>
  );
}
