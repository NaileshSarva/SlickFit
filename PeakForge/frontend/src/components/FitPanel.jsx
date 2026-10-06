import { useState } from "react";

export default function FitPanel({ params, onFit }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleFit() {
    setLoading(true);
    setError("");
    try {
      await onFit();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel workflow-panel">
      <div className="panel-heading">
        <span className="step">Step 3</span>
        <h2>Fit Model</h2>
      </div>

      <button type="button" onClick={handleFit} disabled={loading}>
        {loading ? "Fitting..." : "Fit parameters"}
      </button>

      {error && <p className="inline-error">{error}</p>}

      {params ? (
        <dl className="metrics-grid">
          <div><dt>k1</dt><dd>{params.k1.toFixed(3)}</dd></div>
          <div><dt>k2</dt><dd>{params.k2.toFixed(3)}</dd></div>
          <div><dt>tau1</dt><dd>{params.tau1.toFixed(0)}d</dd></div>
          <div><dt>tau2</dt><dd>{params.tau2.toFixed(0)}d</dd></div>
          <div><dt>p0</dt><dd>{params.p0.toFixed(2)}</dd></div>
          <div><dt>residual</dt><dd>{params.residual_error.toFixed(2)}</dd></div>
        </dl>
      ) : (
        <p className="muted">Fit after logging at least 5 sessions and 3 matching test dates.</p>
      )}
    </section>
  );
}
