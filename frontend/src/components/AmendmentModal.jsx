import React, { useState } from "react";
import { correctActivity } from "../api.js";

export default function AmendmentModal({ isOpen, onClose, activity, onAmendmentSaved }) {
  const [distanceKm, setDistanceKm] = useState(activity?.distance_km || "");
  const [durationMin, setDurationMin] = useState(
    activity?.duration_seconds ? Math.round(activity.duration_seconds / 60) : ""
  );
  const [rpe, setRpe] = useState(activity?.rpe || activity?.perceived_effort || 5);
  const [notes, setNotes] = useState(activity?.perceived_effort_notes || activity?.notes || "");
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen || !activity) return null;

  async function handleSubmit(e) {
    e.preventDefault();
    if (!reason.trim()) {
      setError("A correction reason is strictly required for data integrity audit trails.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const payload = {
        distance_km: distanceKm !== "" ? Number(distanceKm) : null,
        duration_min: durationMin !== "" ? Number(durationMin) : null,
        perceived_effort: rpe ? Number(rpe) : null,
        notes: notes.trim() || null,
        change_reason: reason.trim(),
      };

      const updated = await correctActivity(activity.id, payload);
      if (onAmendmentSaved) {
        onAmendmentSaved(updated);
      }
      onClose();
    } catch (err) {
      setError(err.message || "Failed to submit activity amendment.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="amendment-title">
      <div className="modal-content">
        <div className="card-header">
          <div>
            <h2 className="card-title" id="amendment-title">Correct Logged Activity</h2>
            <p className="card-subtitle">
              Session on {activity.activity_date || activity.event_date || "logged day"}
            </p>
          </div>
          <button type="button" className="btn btn-secondary btn-sm" onClick={onClose}>
            ✕
          </button>
        </div>

        {error && <div className="alert-banner alert-danger">{error}</div>}

        <div className="alert-banner alert-info" style={{ fontSize: "12px", marginBottom: "16px" }}>
          ℹ️ All amendments create immutable before/after snapshot records in the data audit log.
        </div>

        <form onSubmit={handleSubmit}>
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Distance (km)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                className="form-input"
                value={distanceKm}
                onChange={(e) => setDistanceKm(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Duration (minutes)</label>
              <input
                type="number"
                step="1"
                min="1"
                className="form-input"
                value={durationMin}
                onChange={(e) => setDurationMin(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Session RPE (1 = Easy, 10 = Maximum)</label>
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <input
                type="range"
                min="1"
                max="10"
                className="form-input"
                style={{ flex: 1 }}
                value={rpe}
                onChange={(e) => setRpe(e.target.value)}
              />
              <span className="stat-value" style={{ fontSize: "20px", width: "36px", textAlign: "center" }}>
                {rpe}
              </span>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Notes</label>
            <input
              type="text"
              className="form-input"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label" style={{ color: "var(--accent-primary)", fontWeight: 700 }}>
              Correction Reason (Required for Audit Trail) *
            </label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. GPS error on treadmill; stopped timer late"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              required
            />
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "22px" }}>
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? "Saving..." : "Save Amendment"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
