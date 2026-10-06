import React, { useState, useEffect } from "react";
import { getProgressTrends, getUnifiedHistory } from "../api.js";
import VolumeChart from "../components/VolumeChart.jsx";
import RecoveryChart from "../components/RecoveryChart.jsx";
import AmendmentModal from "../components/AmendmentModal.jsx";
import DisclaimerBanner from "../components/DisclaimerBanner.jsx";

export default function Progress({ onRefreshData }) {
  const [trends, setTrends] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeFilter, setActiveFilter] = useState("all");
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [loading, setLoading] = useState(true);

  async function loadData() {
    try {
      const [trendRes, historyRes] = await Promise.all([
        getProgressTrends().catch(() => null),
        getUnifiedHistory().catch(() => []),
      ]);
      setTrends(trendRes);
      setHistory(historyRes || []);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const filteredHistory = history.filter((item) => {
    if (activeFilter === "all") return true;
    if (activeFilter === "activities") return item.item_type === "activity";
    if (activeFilter === "checkins") return item.item_type === "checkin";
    if (activeFilter === "adaptations") return item.item_type === "adaptation";
    if (activeFilter === "amendments") return item.item_type === "amendment";
    return true;
  });

  return (
    <div>
      <DisclaimerBanner type="general" />

      {/* Top Metric Cards */}
      <div className="grid-3" style={{ marginBottom: "22px" }}>
        <div className="stat-box">
          <div className="stat-value" style={{ color: "var(--accent-primary)" }}>
            {trends?.completion_rate !== undefined ? `${trends.completion_rate}%` : "--"}
          </div>
          <div className="stat-label">Plan Adherence Rate</div>
        </div>

        <div className="stat-box">
          <div className="stat-value" style={{ color: "var(--accent-cyan)" }}>
            {trends?.total_completed_km ? `${Number(trends.total_completed_km).toFixed(1)} km` : "0.0 km"}
          </div>
          <div className="stat-label">Total Distance Logged</div>
        </div>

        <div className="stat-box">
          <div className="stat-value" style={{ color: "var(--accent-amber)" }}>
            {trends?.total_activities_count || 0}
          </div>
          <div className="stat-label">Completed Sessions</div>
        </div>
      </div>

      {/* Progress Charts Grid */}
      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">📊 Weekly Volume: Planned vs Completed</h2>
              <p className="card-subtitle">Progressive overload and safe mileage ramp</p>
            </div>
          </div>
          <VolumeChart data={trends?.weekly_volume_trends || []} />
        </div>

        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">🛌 Recovery & Readiness Trajectory</h2>
              <p className="card-subtitle">Sleep quality vs muscle soreness and fatigue</p>
            </div>
          </div>
          <RecoveryChart data={trends?.recent_checkins || []} />
        </div>
      </div>

      {/* Unified Chronological History Feed */}
      <div className="card" style={{ marginTop: "22px" }}>
        <div className="card-header" style={{ flexWrap: "wrap", gap: "12px" }}>
          <div>
            <h2 className="card-title">📜 Unified Chronological Event History</h2>
            <p className="card-subtitle">
              Audit trail of workouts, check-ins, adaptations, and data corrections
            </p>
          </div>

          {/* Filter Pills */}
          <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
            {[
              { key: "all", label: "All Events" },
              { key: "activities", label: "Workouts" },
              { key: "checkins", label: "Check-Ins" },
              { key: "adaptations", label: "Adaptations" },
              { key: "amendments", label: "Amendments" },
            ].map((f) => (
              <button
                key={f.key}
                type="button"
                className={`btn btn-sm ${activeFilter === f.key ? "btn-primary" : "btn-secondary"}`}
                onClick={() => setActiveFilter(f.key)}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "16px" }}>
          {filteredHistory.length === 0 ? (
            <p className="muted" style={{ textAlign: "center", padding: "30px 0" }}>
              No history items match the selected filter.
            </p>
          ) : (
            filteredHistory.map((item, idx) => (
              <div
                key={`${item.item_type}-${item.id || idx}`}
                style={{
                  padding: "16px 18px",
                  borderRadius: "var(--radius-md)",
                  background: "rgba(0,0,0,0.3)",
                  border: "1px solid var(--border-subtle)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  flexWrap: "wrap",
                  gap: "12px",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                  <span style={{ fontSize: "22px" }}>
                    {item.item_type === "activity" && "🏃‍♂️"}
                    {item.item_type === "checkin" && "🛌"}
                    {item.item_type === "adaptation" && "🔄"}
                    {item.item_type === "amendment" && "✏️"}
                  </span>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                      <strong style={{ fontSize: "14px", color: "var(--text-primary)" }}>
                        {item.title || item.summary || `${item.item_type?.toUpperCase()} Event`}
                      </strong>
                      <span
                        className={`tag ${
                          item.item_type === "activity"
                            ? "tag-orange"
                            : item.item_type === "checkin"
                            ? "tag-cyan"
                            : item.item_type === "adaptation"
                            ? "tag-amber"
                            : "tag-neutral"
                        }`}
                      >
                        {item.item_type}
                      </span>
                    </div>
                    <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "3px" }}>
                      {item.details || item.description || item.perceived_effort_notes || "Logged event"}
                    </p>
                  </div>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    {item.event_date || item.created_at?.slice(0, 10)}
                  </span>

                  {item.item_type === "activity" && (
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={() => setSelectedActivity(item)}
                      title="Correct logged activity with required audit reason"
                    >
                      ✏️ Amend
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Amendment Modal */}
      {selectedActivity && (
        <AmendmentModal
          isOpen={Boolean(selectedActivity)}
          activity={selectedActivity}
          onClose={() => setSelectedActivity(null)}
          onAmendmentSaved={() => {
            loadData();
            if (onRefreshData) onRefreshData();
          }}
        />
      )}
    </div>
  );
}
