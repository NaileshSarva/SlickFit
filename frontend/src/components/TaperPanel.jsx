import { useState } from "react";

export default function TaperPanel({ result, onRun, disabled }) {
  const [days, setDays] = useState(21);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleRun(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await onRun(Number(days));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="panel workflow-panel" onSubmit={handleRun}>
      <div className="panel-heading">
        <span className="step">Step 4</span>
        <h2>Optimize Taper</h2>
      </div>

      <label>
        Days until event
        <input
          type="number"
          min="1"
          value={days}
          onChange={(event) => setDays(event.target.value)}
        />
      </label>

      <button type="submit" disabled={disabled || loading}>
        {loading ? "Optimizing..." : "Run optimizer"}
      </button>

      {disabled && <p className="muted">Fit parameters before running the optimizer.</p>}
      {error && <p className="inline-error">{error}</p>}

      {result && (
        <div className="taper-output">
          <div>
            <span className="metric-label">Predicted peak</span>
            <strong>{result.predicted_peak_performance.toFixed(2)}</strong>
          </div>
          <ol className="load-plan">
            {result.best_loads.map((load, index) => (
              <li key={`${index}-${load}`}>
                <span>Day {index + 1}</span>
                <strong>{load.toFixed(1)}</strong>
              </li>
            ))}
          </ol>
        </div>
      )}
    </form>
  );
}
