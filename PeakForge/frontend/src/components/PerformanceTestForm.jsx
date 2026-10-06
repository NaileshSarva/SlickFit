import { useState } from "react";

const today = new Date().toISOString().slice(0, 10);

export default function PerformanceTestForm({ onSubmit }) {
  const [form, setForm] = useState({ date: today, score: "" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");

    try {
      await onSubmit({ date: form.date, score: Number(form.score) });
      setForm((current) => ({ ...current, score: "" }));
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="panel workflow-panel" onSubmit={handleSubmit}>
      <div className="panel-heading">
        <span className="step">Step 2</span>
        <h2>Log Test</h2>
      </div>

      <label>
        Date
        <input type="date" value={form.date} onChange={(event) => updateField("date", event.target.value)} />
      </label>

      <label>
        Score
        <input
          type="number"
          step="0.1"
          value={form.score}
          onChange={(event) => updateField("score", event.target.value)}
          required
        />
      </label>

      {error && <p className="inline-error">{error}</p>}
      <button type="submit" disabled={saving}>{saving ? "Logging..." : "Add test"}</button>
    </form>
  );
}
