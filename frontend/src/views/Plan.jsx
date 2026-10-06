import React, { useState, useEffect } from "react";
import { getCurrentPlan, getPlanHistory } from "../api.js";
import DisclaimerBanner from "../components/DisclaimerBanner.jsx";

export default function Plan({
  currentPlan: initialPlan,
  activeEvent,
  onNavigateTab,
  onRefreshData,
}) {
  const [plan, setPlan] = useState(initialPlan || null);
  const [loading, setLoading] = useState(!initialPlan);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);
  const [historyError, setHistoryError] = useState("");
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [expandedSessionId, setExpandedSessionId] = useState(null);

  // Sync plan if parent updates it
  useEffect(() => {
    if (initialPlan) {
      setPlan(initialPlan);
      setLoading(false);
      setError("");
    }
  }, [initialPlan]);

  // Load plan directly if not provided by parent or on mount
  async function loadPlanData() {
    setLoading(true);
    setError("");
    try {
      const planData = await getCurrentPlan();
      setPlan(planData);
    } catch (err) {
      // 404 means no active plan created yet
      if (err.message && err.message.includes("404")) {
        setPlan(null);
      } else {
        setError(err.message || "Failed to load active training plan.");
      }
    } finally {
      setLoading(false);
    }
  }

  // Load revision history non-blocking (failure must not crash plan screen)
  async function loadHistory() {
    setHistoryError("");
    try {
      const histData = await getPlanHistory();
      setHistory(histData || []);
    } catch (err) {
      setHistoryError("Could not retrieve revision history audit trail.");
      setHistory([]);
    }
  }

  useEffect(() => {
    if (!initialPlan) {
      loadPlanData();
    }
    loadHistory();
  }, []);

  const todayStr = new Date().toISOString().slice(0, 10);
  const sessions = plan?.sessions || [];
  const currentRev = plan?.current_revision || null;

  // Safe Date Formatting Helpers
  function formatDayBadge(dateString) {
    if (!dateString) return { weekday: "DAY", dayNum: "--", full: "" };
    try {
      const d = new Date(dateString + "T00:00:00");
      if (isNaN(d.getTime())) return { weekday: "DAY", dayNum: dateString.slice(-2) || "--", full: dateString };
      
      const weekday = d.toLocaleDateString("en-US", { weekday: "short" });
      const day = d.getDate();
      const suffix =
        day % 10 === 1 && day !== 11
          ? "st"
          : day % 10 === 2 && day !== 12
          ? "nd"
          : day % 10 === 3 && day !== 13
          ? "rd"
          : "th";
      
      const full = d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
      return { weekday, dayNum: `${day}${suffix}`, full };
    } catch {
      return { weekday: "DAY", dayNum: "--", full: dateString };
    }
  }

  function formatPace(secPerKm) {
    if (!secPerKm || typeof secPerKm !== "number") return null;
    const mins = Math.floor(secPerKm / 60);
    const secs = Math.round(secPerKm % 60);
    return `${mins}:${secs.toString().padStart(2, "0")} /km`;
  }

  function formatDistance(session) {
    const min = session.distance_km_min;
    const max = session.distance_km_max;
    if (min != null && max != null) {
      return min === max ? `${min} km` : `${min}–${max} km`;
    }
    if (max != null) return `${max} km`;
    if (min != null) return `${min} km`;
    if (session.planned_distance_km != null) return `${session.planned_distance_km} km`;
    return null;
  }

  function formatDuration(session) {
    const min = session.duration_min_min;
    const max = session.duration_min_max;
    if (min != null && max != null) {
      return min === max ? `${min} min` : `${min}–${max} min`;
    }
    if (max != null) return `${max} min`;
    if (min != null) return `${min} min`;
    if (session.planned_duration_minutes != null) return `${session.planned_duration_minutes} min`;
    return null;
  }

  function getSessionTypeInfo(type) {
    switch (type) {
      case "rest":
        return { label: "Active Recovery", tagClass: "tag-neutral", icon: "🛌", isRest: true };
      case "recovery_walk":
        return { label: "Recovery Walk", tagClass: "tag-neutral", icon: "🚶", isRest: true };
      case "long_run":
        return { label: "Long Run", tagClass: "tag-amber", icon: "🏃‍♂️", isRest: false };
      case "intervals":
      case "interval":
        return { label: "Intervals", tagClass: "tag-cyan", icon: "⚡", isRest: false };
      case "tempo":
        return { label: "Tempo Run", tagClass: "tag-orange", icon: "🔥", isRest: false };
      case "walk_run":
        return { label: "Walk-Run Build", tagClass: "tag-emerald", icon: "👟", isRest: false };
      case "easy_run":
      default:
        return { label: "Easy Run", tagClass: "tag-emerald", icon: "🏃", isRest: false };
    }
  }

  // Parse Macro Phases
  let phases = [
    { name: "Foundation & Base", desc: "Builds aerobic capacity and tendon durability safely", active: true },
    { name: "Build & Tempo", desc: "Introduces threshold pacing and volume progression", active: false },
    { name: "Peak & Specificity", desc: "Race-pace rehearsal and peak physiological readiness", active: false },
    { name: "Taper & Sharpen", desc: "Controlled volume reduction for freshness on race day", active: false },
  ];

  if (currentRev?.phases_json) {
    try {
      const parsed = JSON.parse(currentRev.phases_json);
      if (Array.isArray(parsed) && parsed.length > 0) {
        phases = parsed.map((p, idx) => ({
          name: p.name || `Phase ${idx + 1}`,
          desc: p.focus || (p.weekly_mileage_target_km ? `Target: ~${p.weekly_mileage_target_km} km/wk` : "Target phase progression"),
          active: Boolean(p.current || idx === 0),
        }));
      }
    } catch {
      // Keep default phases fallback
    }
  }

  // Loading State
  if (loading) {
    return (
      <div>
        <DisclaimerBanner type="general" />
        <div className="state-container">
          <div className="spinner" />
          <h2 style={{ fontSize: "18px", marginBottom: "8px" }}>Loading 7-Day Training Plan</h2>
          <p className="muted">Fetching deterministic microcycle and safety parameters...</p>
        </div>
      </div>
    );
  }

  // Error State with Retry
  if (error) {
    return (
      <div>
        <DisclaimerBanner type="general" />
        <div className="state-container">
          <div className="state-icon-orb" style={{ background: "var(--accent-crimson-dim)", borderColor: "rgba(239, 68, 68, 0.4)" }}>
            ⚠️
          </div>
          <h2 style={{ fontSize: "20px", marginBottom: "8px" }}>Unable to Load Training Plan</h2>
          <p className="muted" style={{ maxWidth: "480px", marginBottom: "20px" }}>{error}</p>
          <div style={{ display: "flex", gap: "12px" }}>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => {
                loadPlanData();
                if (onRefreshData) onRefreshData();
              }}
            >
              🔄 Retry Request
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => onNavigateTab("home")}
            >
              Return to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Empty State (No plan created yet)
  if (!plan) {
    return (
      <div>
        <DisclaimerBanner type="general" />
        <div className="state-container">
          <div className="state-icon-orb">📅</div>
          <h2 style={{ fontSize: "22px", marginBottom: "10px" }}>No Active Training Plan Found</h2>
          <p className="muted" style={{ maxWidth: "520px", marginBottom: "24px" }}>
            SlickFit generates a personalized, safety-bounded 7-day microcycle once your target event and baseline availability are registered.
          </p>
          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap", justifyContent: "center" }}>
            <button
              type="button"
              className="btn btn-primary btn-lg"
              onClick={() => onNavigateTab("profile")}
            >
              Configure Target Event & Availability →
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => {
                loadPlanData();
                if (onRefreshData) onRefreshData();
              }}
            >
              Check Again 🔄
            </button>
          </div>
        </div>
      </div>
    );
  }

  const eventTitle = plan.event_title || activeEvent?.title || "Target Event";
  const daysUntilEvent = plan.days_until_event != null ? plan.days_until_event : (activeEvent?.event_date ? Math.max(0, Math.ceil((new Date(activeEvent.event_date) - new Date()) / (1000 * 60 * 60 * 24))) : null);
  const targetDist = activeEvent?.target_value || activeEvent?.target_distance_km || null;

  return (
    <div>
      <DisclaimerBanner type="general" />

      {/* Hero Plan Header */}
      <div className="hero-card">
        <div className="hero-orb" />
        <div style={{ position: "relative", zIndex: 2 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap", marginBottom: "6px" }}>
                <span className="tag tag-orange">
                  Revision #{currentRev?.revision_number || 1}
                </span>
                <span className="tag tag-espresso">
                  {plan.algorithm_version || "Rule-Based Engine"}
                </span>
                {plan.confidence && (
                  <span className="tag tag-cyan" title="Plan derivation mode">
                    Confidence: {plan.confidence}
                  </span>
                )}
              </div>

              <h1 style={{ fontSize: "28px", fontWeight: 800, marginTop: "6px" }}>
                Active 7-Day Microcycle Plan
              </h1>

              <p style={{ color: "var(--text-secondary)", fontSize: "14px", marginTop: "6px" }}>
                Target Event: <strong style={{ color: "var(--text-primary)" }}>{eventTitle}</strong>
                {targetDist && ` (${targetDist} km)`}
                {daysUntilEvent !== null && ` • ${daysUntilEvent} days remaining`}
              </p>
            </div>

            <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => setShowHistoryModal(true)}
                title="View immutable plan revisions and audit log"
              >
                📜 Revision Audit ({history.length})
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => {
                  loadPlanData();
                  loadHistory();
                  if (onRefreshData) onRefreshData();
                }}
                title="Refresh plan from server"
              >
                🔄
              </button>
            </div>
          </div>

          {/* Explanation / Coach Reasoning */}
          {currentRev?.explanation && (
            <div style={{ marginTop: "18px", padding: "14px 18px", background: "rgba(0,0,0,0.35)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
              <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--accent-primary)", textTransform: "uppercase", letterSpacing: "0.05em", display: "block", marginBottom: "4px" }}>
                Coaching Rationale & Adaptation Trigger
              </span>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.5" }}>
                {currentRev.explanation}
              </p>
            </div>
          )}

          {/* Macro Phase Roadmap */}
          <div style={{ marginTop: "20px", paddingTop: "18px", borderTop: "1px solid var(--border-subtle)" }}>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", display: "block", marginBottom: "10px" }}>
              Macro Periodization Roadmap
            </span>
            <div className="grid-4" style={{ gap: "10px" }}>
              {phases.map((p, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "12px 14px",
                    borderRadius: "var(--radius-md)",
                    background: p.active ? "rgba(255, 109, 41, 0.14)" : "rgba(0, 0, 0, 0.25)",
                    border: p.active ? "1px solid var(--accent-primary)" : "1px solid var(--border-subtle)",
                    transition: "var(--transition-smooth)",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                    <strong style={{ fontSize: "13px", color: p.active ? "var(--accent-primary)" : "var(--text-primary)" }}>
                      {p.name}
                    </strong>
                    {p.active && <span className="tag tag-orange" style={{ padding: "2px 6px", fontSize: "9px" }}>Current</span>}
                  </div>
                  <p style={{ fontSize: "11px", color: "var(--text-secondary)", lineHeight: "1.4" }}>
                    {p.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 7-Day Rolling Schedule Cards */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", marginTop: "10px" }}>
        <div>
          <h2 style={{ fontSize: "20px", fontWeight: 700 }}>Scheduled Sessions This Microcycle</h2>
          <p className="muted">Deterministic daily workouts based on your availability and progressive recovery</p>
        </div>
        <span className="tag tag-neutral">{sessions.length} Scheduled Days</span>
      </div>

      {sessions.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "40px" }}>
          <p className="muted">No scheduled sessions found for the current revision.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          {sessions.map((session, idx) => {
            const dateStr = session.local_date || session.scheduled_date || "";
            const isToday = dateStr === todayStr;
            const dateInfo = formatDayBadge(dateStr);
            const typeInfo = getSessionTypeInfo(session.session_type);
            const distStr = formatDistance(session);
            const durStr = formatDuration(session);
            const paceStr = formatPace(session.target_pace_sec_per_km);
            const isExpanded = expandedSessionId === (session.id || idx);

            // Parse workout blocks if present
            let workoutBlocks = [];
            if (session.blocks_json) {
              try {
                const parsed = JSON.parse(session.blocks_json);
                if (Array.isArray(parsed)) workoutBlocks = parsed;
              } catch {
                // Ignore parse errors
              }
            }

            return (
              <div
                key={session.id || `${dateStr}-${idx}`}
                className={`card-interactive plan-session-row ${isToday ? "today" : ""}`}
                style={{
                  display: "block",
                  padding: "18px 20px",
                  borderRadius: "var(--radius-lg)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
                  {/* Left: Date Badge & Title */}
                  <div style={{ display: "flex", alignItems: "center", gap: "16px", minWidth: "260px" }}>
                    <div className="plan-date-badge">
                      <span className="day-name">{dateInfo.weekday}</span>
                      <span className="day-num">{dateInfo.dayNum}</span>
                    </div>

                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                        <span style={{ fontSize: "16px" }}>{typeInfo.icon}</span>
                        <strong style={{ fontSize: "16px", color: "var(--text-primary)" }}>
                          {session.purpose || typeInfo.label}
                        </strong>
                        <span className={`tag ${typeInfo.tagClass}`}>{typeInfo.label}</span>
                        {isToday && <span className="tag tag-orange">Today</span>}
                        {session.priority === "high" && <span className="tag tag-amber">Key Session</span>}
                      </div>

                      <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "4px" }}>
                        {session.effort_target ? `Effort: ${session.effort_target}` : (typeInfo.isRest ? "Complete active recovery to allow physiological adaptation" : "Aerobic training run")}
                        {session.flexibility_window_days > 0 && ` • Flexible ±${session.flexibility_window_days}d`}
                      </p>
                    </div>
                  </div>

                  {/* Right: Metrics & Action Buttons */}
                  <div style={{ display: "flex", alignItems: "center", gap: "18px", flexWrap: "wrap" }}>
                    {!typeInfo.isRest && (
                      <>
                        {distStr && (
                          <div style={{ textAlign: "center", minWidth: "65px" }}>
                            <div style={{ fontSize: "15px", fontWeight: 700, color: "var(--text-primary)" }}>
                              {distStr}
                            </div>
                            <div style={{ fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase" }}>
                              Distance
                            </div>
                          </div>
                        )}

                        {durStr && (
                          <div style={{ textAlign: "center", minWidth: "65px" }}>
                            <div style={{ fontSize: "15px", fontWeight: 700, color: "var(--text-primary)" }}>
                              {durStr}
                            </div>
                            <div style={{ fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase" }}>
                              Duration
                            </div>
                          </div>
                        )}

                        {paceStr && (
                          <div style={{ textAlign: "center", minWidth: "75px" }}>
                            <div style={{ fontSize: "14px", fontWeight: 700, color: "var(--accent-cyan)" }}>
                              {paceStr}
                            </div>
                            <div style={{ fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase" }}>
                              Target Pace
                            </div>
                          </div>
                        )}
                      </>
                    )}

                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      {workoutBlocks.length > 0 && (
                        <button
                          type="button"
                          className="btn btn-secondary btn-sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            setExpandedSessionId(isExpanded ? null : (session.id || idx));
                          }}
                          title="Toggle workout structure details"
                        >
                          {isExpanded ? "Hide Details ▲" : "Details ▼"}
                        </button>
                      )}

                      {isToday && !typeInfo.isRest ? (
                        <button
                          type="button"
                          className="btn btn-primary btn-sm"
                          onClick={() => onNavigateTab("train")}
                        >
                          Start Workout →
                        </button>
                      ) : !typeInfo.isRest ? (
                        <button
                          type="button"
                          className="btn btn-secondary btn-sm"
                          onClick={() => onNavigateTab("train")}
                        >
                          View in Train →
                        </button>
                      ) : null}
                    </div>
                  </div>
                </div>

                {/* Expanded Details: Workout Structure Blocks */}
                {isExpanded && workoutBlocks.length > 0 && (
                  <div style={{ marginTop: "16px", paddingTop: "14px", borderTop: "1px solid var(--border-subtle)" }}>
                    <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--accent-primary)", textTransform: "uppercase", letterSpacing: "0.05em", display: "block", marginBottom: "8px" }}>
                      Structured Workout Progression
                    </span>
                    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                      {workoutBlocks.map((blk, bIdx) => (
                        <div
                          key={bIdx}
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            padding: "10px 14px",
                            borderRadius: "var(--radius-sm)",
                            background: "rgba(255, 255, 255, 0.03)",
                            border: "1px solid var(--border-subtle)",
                          }}
                        >
                          <div>
                            <strong style={{ fontSize: "13px", color: "var(--text-primary)", textTransform: "capitalize" }}>
                              {blk.name?.replace("_", " ") || `Block ${bIdx + 1}`}
                            </strong>
                            <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "2px" }}>
                              {blk.description}
                            </p>
                          </div>
                          {blk.duration_min && (
                            <span className="tag tag-neutral">{blk.duration_min} min</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Revision History Audit Modal */}
      {showHistoryModal && (
        <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="history-modal-title">
          <div className="modal-content" style={{ maxWidth: "720px" }}>
            <div className="card-header">
              <div>
                <h2 className="card-title" id="history-modal-title">📜 Plan Revision Audit History</h2>
                <p className="card-subtitle">
                  Every plan change is snapshot-hashed and accompanied by a deterministic reasoning trigger.
                </p>
              </div>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => setShowHistoryModal(false)}
              >
                ✕
              </button>
            </div>

            {historyError && <div className="alert-banner alert-warning">{historyError}</div>}

            <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "16px" }}>
              {history.length === 0 ? (
                <div style={{ textAlign: "center", padding: "30px", color: "var(--text-muted)" }}>
                  No prior revisions recorded. You are on initial baseline revision #1.
                </div>
              ) : (
                history.map((rev) => (
                  <div
                    key={rev.id || rev.revision_number}
                    style={{
                      padding: "16px",
                      borderRadius: "var(--radius-md)",
                      background: "rgba(0,0,0,0.35)",
                      border: "1px solid var(--border-subtle)",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
                      <div>
                        <strong style={{ fontSize: "15px", color: "var(--text-primary)" }}>
                          Revision #{rev.revision_number}
                        </strong>
                        <span style={{ fontSize: "12px", color: "var(--text-muted)", marginLeft: "10px" }}>
                          {rev.created_at ? new Date(rev.created_at).toLocaleString() : ""}
                        </span>
                      </div>
                      <span className="tag tag-cyan">{rev.trigger_reason || rev.reason_code || "SCHEDULE_UPDATE"}</span>
                    </div>

                    <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "8px", lineHeight: "1.5" }}>
                      {rev.explanation || rev.coach_reasoning || "Plan microcycle adjusted to match athlete baseline."}
                    </p>

                    {rev.input_snapshot_hash && (
                      <div style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "monospace", marginTop: "8px" }}>
                        Snapshot SHA-256: {rev.input_snapshot_hash.slice(0, 20)}...
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "24px" }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowHistoryModal(false)}
              >
                Close Audit Log
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
