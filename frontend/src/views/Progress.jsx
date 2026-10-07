import React, { useState, useEffect } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import { getProgressTrends, getUnifiedHistory } from "../api.js";
import VolumeChart from "../components/VolumeChart.jsx";
import AmendmentModal from "../components/AmendmentModal.jsx";
import DisclaimerBanner from "../components/DisclaimerBanner.jsx";

/**
 * Inline chart for recent_runs from /progress:
 *   [{date, duration_min, distance_km, pace_min_km, effort}]
 */
function RecentRunsChart({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "40px 20px", color: "var(--text-muted)" }}>
        No recent runs recorded yet. Log your first session to see trends here.
      </div>
    );
  }

  const chartData = data.map((r) => ({
    date: r.date?.slice(5) || "–",
    pace: r.pace_min_km != null ? Number(r.pace_min_km).toFixed(1) : null,
    effort: r.effort ?? null,
  }));

  return (
    <div style={{ width: "100%", height: 260 }}>
      <ResponsiveContainer>
        <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={12} tickLine={false} />
          <YAxis
            yAxisId="pace"
            orientation="left"
            stroke="var(--text-muted)"
            fontSize={12}
            tickLine={false}
            unit=" m/k"
          />
          <YAxis
            yAxisId="effort"
            orientation="right"
            stroke="var(--text-muted)"
            fontSize={12}
            tickLine={false}
            domain={[1, 10]}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(22, 19, 22, 0.95)",
              borderColor: "rgba(255, 255, 255, 0.12)",
              borderRadius: "12px",
              color: "var(--text-primary)",
              boxShadow: "0 12px 30px rgba(0,0,0,0.6)",
            }}
          />
          <Legend
            wrapperStyle={{ paddingTop: "10px", fontSize: "12px" }}
            formatter={(v) => (v === "pace" ? "Pace (min/km)" : "Effort (1–10)")}
          />
          <Line
            yAxisId="pace"
            type="monotone"
            dataKey="pace"
            stroke="var(--accent-cyan)"
            strokeWidth={2.5}
            dot={{ r: 4, fill: "var(--accent-cyan)" }}
            connectNulls
          />
          <Line
            yAxisId="effort"
            type="monotone"
            dataKey="effort"
            stroke="var(--accent-amber)"
            strokeWidth={2}
            strokeDasharray="4 4"
            dot={{ r: 3, fill: "var(--accent-amber)" }}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

/**
 * Progress view.
 * API shape from /progress:
 *   total_runs_completed, total_distance_km, total_duration_min,
 *   consistency_rate_pct, recent_runs[], weekly_mileage_series[]
 */
export default function Progress({ onRefreshData }) {
  const [trends, setTrends] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeFilter, setActiveFilter] = useState("all");
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [trendsError, setTrendsError] = useState(null);
  const [historyError, setHistoryError] = useState(null);

  async function loadData() {
    setLoading(true);
    setTrendsError(null);
    setHistoryError(null);

    const [trendResult, historyResult] = await Promise.allSettled([
      getProgressTrends(),
      getUnifiedHistory(),
    ]);

    if (trendResult.status === "fulfilled") {
      setTrends(trendResult.value);
    } else {
      setTrendsError(trendResult.reason?.message || "Could not load progress trends.");
      setTrends(null);
    }

    if (historyResult.status === "fulfilled") {
      setHistory(Array.isArray(historyResult.value) ? historyResult.value : []);
    } else {
      setHistoryError(historyResult.reason?.message || "Could not load activity history.");
      setHistory([]);
    }

    setLoading(false);
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

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "60px 20px", color: "var(--text-muted)" }}>
        <p>Loading your progress data…</p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      <DisclaimerBanner type="general" />

      {/* Trends error with retry */}
      {trendsError && (
        <div
          style={{
            padding: "14px 18px",
            borderRadius: "var(--radius-md)",
            background: "rgba(239,68,68,0.1)",
            border: "1px solid rgba(239,68,68,0.3)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "10px",
          }}
        >
          <span style={{ color: "var(--accent-crimson)", fontSize: "14px" }}>{trendsError}</span>
          <button type="button" className="btn btn-secondary btn-sm" onClick={loadData}>
            Retry
          </button>
        </div>
      )}

      {/* Top Metric Cards */}
      {trends ? (
        <div className="grid-3">
          <div className="stat-box">
            <div className="stat-value" style={{ color: "var(--accent-primary)" }}>
              {trends.consistency_rate_pct != null
                ? `${Number(trends.consistency_rate_pct).toFixed(1)}%`
                : "--"}
            </div>
            <div className="stat-label">Consistency Rate</div>
          </div>
          <div className="stat-box">
            <div className="stat-value" style={{ color: "var(--accent-cyan)" }}>
              {trends.total_distance_km != null
                ? `${Number(trends.total_distance_km).toFixed(1)} km`
                : "0.0 km"}
            </div>
            <div className="stat-label">Total Distance Logged</div>
          </div>
          <div className="stat-box">
            <div className="stat-value" style={{ color: "var(--accent-amber)" }}>
              {trends.total_runs_completed ?? 0}
            </div>
            <div className="stat-label">Completed Sessions</div>
          </div>
        </div>
      ) : !trendsError ? (
        <div className="stat-box" style={{ textAlign: "center", padding: "24px" }}>
          <p className="muted">No progress metrics yet. Complete sessions to start tracking.</p>
        </div>
      ) : null}

      {/* Charts */}
      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Weekly Training Volume</h2>
              <p className="card-subtitle">Distance completed per training week</p>
            </div>
          </div>
          <VolumeChart data={trends?.weekly_mileage_series ?? []} />
        </div>

        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Recent Session Efforts</h2>
              <p className="card-subtitle">Pace and effort across your last sessions</p>
            </div>
          </div>
          <RecentRunsChart data={trends?.recent_runs ?? []} />
        </div>
      </div>

      {/* Unified History Feed */}
      <div className="card">
        <div className="card-header" style={{ flexWrap: "wrap", gap: "12px" }}>
          <div>
            <h2 className="card-title">Unified Chronological Event History</h2>
            <p className="card-subtitle">
              Audit trail of workouts, check-ins, adaptations, and data corrections
            </p>
          </div>
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

        {historyError && (
          <div style={{ display: "flex", alignItems: "center", gap: "12px", padding: "10px 0", fontSize: "13px" }}>
            <span style={{ color: "var(--accent-crimson)" }}>{historyError}</span>
            <button type="button" className="btn btn-secondary btn-sm" onClick={loadData}>Retry</button>
          </div>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "16px" }}>
          {filteredHistory.length === 0 ? (
            <p className="muted" style={{ textAlign: "center", padding: "30px 0" }}>
              {historyError ? "History unavailable. Use Retry above." : "No history items match the selected filter."}
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
                      {item.summary ||
                        (typeof item.details === "object" && item.details !== null
                          ? item.details.notes || item.details.early_stop_reason || ""
                          : item.details) ||
                        item.description ||
                        item.perceived_effort_notes ||
                        "Logged event"}
                    </p>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    {item.local_date || item.event_date || item.timestamp?.slice(0, 10) || item.created_at?.slice(0, 10)}
                  </span>
                  {item.item_type === "activity" && (
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={() => setSelectedActivity(item)}
                      title="Correct logged activity with required audit reason"
                    >
                      Amend
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

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
