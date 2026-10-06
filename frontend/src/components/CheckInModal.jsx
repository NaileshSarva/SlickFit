import React, { useState } from "react";
import { recordCheckIn } from "../api.js";

export default function CheckInModal({ isOpen, onClose, onCheckInRecorded, initialData = null }) {
  const [sleepQuality, setSleepQuality] = useState(initialData?.sleep_quality || 4);
  const [soreness, setSoreness] = useState(initialData?.soreness_level || initialData?.soreness || 2);
  const [stress, setStress] = useState(initialData?.stress_level || initialData?.stress || 2);
  const [fatigue, setFatigue] = useState(initialData?.fatigue || 2);
  const [hasPain, setHasPain] = useState(initialData?.pain_flag || initialData?.pain_reported || false);
  const [painLocation, setPainLocation] = useState(initialData?.pain_area || initialData?.pain_location || "");
  const [painSeverity, setPainSeverity] = useState(initialData?.pain_severity || 1);
  const [hasRedFlags, setHasRedFlags] = useState(initialData?.red_flag_symptom || initialData?.red_flag_symptoms || false);
  const [notes, setNotes] = useState(initialData?.notes || "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const payload = {
        local_date: new Date().toISOString().slice(0, 10),
        sleep_quality: Number(sleepQuality),
        energy_level: Math.max(1, Math.min(5, 6 - Number(fatigue))),
        soreness_level: Number(soreness),
        stress_level: Number(stress),
        pain_flag: Boolean(hasPain),
        pain_area: hasPain ? (painLocation.trim() || "Musculoskeletal") : "",
        pain_severity: hasPain ? Number(painSeverity) : 0,
        red_flag_symptom: Boolean(hasRedFlags),
        notes: notes.trim() || "",
      };

      const result = await recordCheckIn(payload);
      if (onCheckInRecorded) {
        onCheckInRecorded(result);
      }
      onClose();
    } catch (err) {
      setError(err.message || "Failed to record check-in.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="checkin-title">
      <div className="modal-content">
        <div className="card-header">
          <div>
            <h2 className="card-title" id="checkin-title">Daily Recovery & Readiness Check-In</h2>
            <p className="card-subtitle">Quick check to evaluate fatigue and adapt today's training load</p>
          </div>
          <button type="button" className="btn btn-secondary btn-sm" onClick={onClose}>
            ✕
          </button>
        </div>

        {error && <div className="alert-banner alert-danger">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Sleep Quality (1 = Poor, 5 = Deep)</label>
              <select
                className="form-select"
                value={sleepQuality}
                onChange={(e) => setSleepQuality(e.target.value)}
              >
                <option value="1">1 - Restless / Insomnia</option>
                <option value="2">2 - Poor / Interrupted</option>
                <option value="3">3 - Fair / Average</option>
                <option value="4">4 - Good / Rested</option>
                <option value="5">5 - Optimal / Deep Sleep</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Muscle Soreness (1 = Fresh, 5 = Severe)</label>
              <select
                className="form-select"
                value={soreness}
                onChange={(e) => setSoreness(e.target.value)}
              >
                <option value="1">1 - Fresh / No Soreness</option>
                <option value="2">2 - Mild / Normal Tone</option>
                <option value="3">3 - Moderate Soreness</option>
                <option value="4">4 - High Soreness / Tight</option>
                <option value="5">5 - Severe Soreness / Impaired</option>
              </select>
            </div>
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Life / Work Stress (1 = Calm, 5 = High)</label>
              <select
                className="form-select"
                value={stress}
                onChange={(e) => setStress(e.target.value)}
              >
                <option value="1">1 - Relaxed / Calm</option>
                <option value="2">2 - Low / Manageable</option>
                <option value="3">3 - Moderate Stress</option>
                <option value="4">4 - High Stress</option>
                <option value="5">5 - Overwhelmed</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Fatigue / Drain (1 = Energized, 5 = Exhausted)</label>
              <select
                className="form-select"
                value={fatigue}
                onChange={(e) => setFatigue(e.target.value)}
              >
                <option value="1">1 - Highly Energized</option>
                <option value="2">2 - Normal Energy</option>
                <option value="3">3 - Slightly Tired</option>
                <option value="4">4 - Heavy Fatigue</option>
                <option value="5">5 - Exhausted</option>
              </select>
            </div>
          </div>

          <div style={{ padding: "14px", background: "rgba(0,0,0,0.3)", borderRadius: "var(--radius-md)", marginBottom: "16px" }}>
            <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer", fontWeight: 600, fontSize: "13px" }}>
              <input
                type="checkbox"
                checked={hasPain}
                onChange={(e) => setHasPain(e.target.checked)}
                style={{ width: "16px", height: "16px", accentColor: "var(--accent-amber)" }}
              />
              <span>Report Musculoskeletal Pain or Joint Discomfort</span>
            </label>

            {hasPain && (
              <div className="grid-2" style={{ marginTop: "12px" }}>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Pain Location</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Left Achilles, Right Knee, Shin"
                    value={painLocation}
                    onChange={(e) => setPainLocation(e.target.value)}
                    required={hasPain}
                  />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Pain Severity (1-10)</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    className="form-input"
                    value={painSeverity}
                    onChange={(e) => setPainSeverity(e.target.value)}
                  />
                </div>
              </div>
            )}
          </div>

          <div style={{ padding: "14px", background: "var(--accent-crimson-dim)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: "var(--radius-md)", marginBottom: "20px" }}>
            <label style={{ display: "flex", alignItems: "flex-start", gap: "10px", cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={hasRedFlags}
                onChange={(e) => setHasRedFlags(e.target.checked)}
                style={{ width: "18px", height: "18px", accentColor: "var(--accent-crimson)", marginTop: "2px" }}
              />
              <div>
                <span style={{ color: "var(--accent-crimson)", fontWeight: 700, fontSize: "13px" }}>
                  RED-FLAG SYMPTOMS (Chest Pain, Dizziness, Shortness of Breath, Acute Trauma)
                </span>
                <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "2px" }}>
                  Checking this immediately stops all workout prescriptions and locks training for safety.
                </p>
              </div>
            </label>
          </div>

          <div className="form-group">
            <label className="form-label">Optional Notes</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Slept late due to travel, mild hydration deficit"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "22px" }}>
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? "Recording..." : "Save Check-In"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
