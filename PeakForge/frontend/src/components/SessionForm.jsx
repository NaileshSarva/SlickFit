import { useState } from "react";

const today = new Date().toISOString().slice(0, 10);

export default function SessionForm({ onSubmit }) {
  const [form, setForm] = useState({
    date: today,
    duration_min: 60,
    intensity: 6,
    notes: "",
  });
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
      await onSubmit({
        ...form,
        duration_min: Number(form.duration_min),
        intensity: Number(form.intensity),
      });
      setForm((current) => ({ ...current, notes: "" }));
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="panel workflow-panel" onSubmit={handleSubmit}>
      <div className="panel-heading">
        <span className="step">Step 1</span>
        <h2>Log Training</h2>
      </div>

      <label>
        Date
        <input type="date" value={form.date} onChange={(event) => updateField("date", event.target.value)} />
      </label>

      <div className="field-row">
        <label>
          Duration
          <input
            type="number"
            min="1"
            value={form.duration_min}
            onChange={(event) => updateField("duration_min", event.target.value)}
          />
        </label>
        <label>
          Intensity
          <input
            type="number"
            min="0.1"
            step="0.1"
            value={form.intensity}
            onChange={(event) => updateField("intensity", event.target.value)}
          />
        </label>
      </div>

      <label>
        Notes
        <input value={form.notes} onChange={(event) => updateField("notes", event.target.value)} />
      </label>

      {error && <p className="inline-error">{error}</p>}
      <button type="submit" disabled={saving}>{saving ? "Logging..." : "Add session"}</button>
    </form>
  );
}
