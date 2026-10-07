import React, { useState, useEffect } from "react";
import CheckInModal from "../components/CheckInModal.jsx";
import DisclaimerBanner from "../components/DisclaimerBanner.jsx";
import { getProgressTrends } from "../api.js";

export default function Home({
  user,
  activeEvent,
  currentPlan,
  todayCheckIn,
  todayNutrition,
  onNavigateTab,
  onRefreshData,
}) {
  const [showCheckInModal, setShowCheckInModal] = useState(false);
  const [trends, setTrends] = useState(null);
  const [timeFilter, setTimeFilter] = useState("week");

  useEffect(() => {
    getProgressTrends()
      .then((res) => setTrends(res))
      .catch(() => setTrends(null));
  }, []);

  // Today's Date and Session
  const todayDateObj = new Date();
  const todayStr = todayDateObj.toISOString().slice(0, 10);
  const todayFormatted = todayDateObj.toLocaleDateString("en-US", {
    weekday: "long",
    day: "numeric",
    month: "short",
  });

  const sessions = currentPlan?.sessions || [];
  const todaySession =
    sessions.find((s) => (s.local_date || s.scheduled_date) === todayStr) ||
    sessions[0] ||
    null;

  const eventDateStr = activeEvent?.event_date || activeEvent?.target_date || currentPlan?.event_date;
  const eventDaysLeft = eventDateStr
    ? Math.max(0, Math.ceil((new Date(eventDateStr + "T00:00:00") - new Date()) / (1000 * 60 * 60 * 24)))
    : (currentPlan?.days_until_event != null ? currentPlan.days_until_event : null);

  const isRedFlagActive = Boolean(
    todayCheckIn?.red_flag_symptom ||
    currentPlan?.current_revision?.explanation?.includes("URGENT SAFETY STOP") ||
    currentPlan?.current_revision?.trigger_reason === "RED_FLAG_SAFETY_STOP"
  );

  const eventDist = activeEvent?.target_value || activeEvent?.target_distance_km || null;
  const athleteName = user?.full_name?.split(" ")[0] || user?.email?.split("@")[0] || "Athlete";

  // Format Helper for Distance
  function formatDist(s) {
    if (!s) return "--";
    if (s.distance_km_min != null && s.distance_km_max != null) {
      return s.distance_km_min === s.distance_km_max ? `${s.distance_km_min} km` : `${s.distance_km_min}–${s.distance_km_max} km`;
    }
    if (s.distance_km_max != null) return `${s.distance_km_max} km`;
    if (s.distance_km_min != null) return `${s.distance_km_min} km`;
    if (s.planned_distance_km != null) return `${s.planned_distance_km} km`;
    return "--";
  }

  // Format Helper for Duration
  function formatDur(s) {
    if (!s) return "--";
    if (s.duration_min_min != null && s.duration_min_max != null) {
      return s.duration_min_min === s.duration_min_max ? `${s.duration_min_min}m` : `${s.duration_min_min}–${s.duration_min_max}m`;
    }
    if (s.duration_min_max != null) return `${s.duration_min_max}m`;
    if (s.duration_min_min != null) return `${s.duration_min_min}m`;
    if (s.planned_duration_minutes != null) return `${s.planned_duration_minutes}m`;
    return "--";
  }

  function formatPace(secPerKm) {
    if (!secPerKm || typeof secPerKm !== "number") return "Zone 2 Effort";
    const mins = Math.floor(secPerKm / 60);
    const secs = Math.round(secPerKm % 60);
    return `${mins}:${secs.toString().padStart(2, "0")} /km`;
  }

  // Calculate readiness score (1 - 10)
  const sleepVal = todayCheckIn?.sleep_quality || 4;
  const sorenessVal = todayCheckIn?.soreness_level || todayCheckIn?.soreness || 2;
  const stressVal = todayCheckIn?.stress_level || todayCheckIn?.stress || 2;
  const energyVal = todayCheckIn?.energy_level || 3;
  const readinessScore = Number((((sleepVal + (6 - sorenessVal) + (6 - stressVal) + energyVal) / 20) * 10).toFixed(1));

  // 7-Day Histogram distribution calculation
  const weekDays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const miniBarData = sessions.length === 7
    ? sessions.map((s) => {
        const d = new Date(s.local_date + "T00:00:00");
        const dayIdx = isNaN(d.getTime()) ? 0 : (d.getDay() + 6) % 7;
        const dayLabel = weekDays[dayIdx] || "Day";
        const isSessToday = s.local_date === todayStr;
        const dist = s.distance_km_max || s.distance_km_min || 0;
        const isRest = s.session_type === "rest";
        const heightPct = isRest ? 15 : Math.max(25, Math.min(100, (dist / 10) * 100));
        return { dayLabel, isSessToday, isRest, heightPct, dist };
      })
    : weekDays.map((d, i) => ({
        dayLabel: d,
        isSessToday: i === (todayDateObj.getDay() + 6) % 7,
        isRest: i % 2 === 0,
        heightPct: i % 2 === 0 ? 15 : 60,
        dist: i % 2 === 0 ? 0 : 5,
      }));

  return (
    <div>
      <DisclaimerBanner type="general" />

      {/* Top Athlete Greeting Bar */}
      <div className="dashboard-header-bar">
        <div>
          <h1 className="dashboard-greeting-title">
            Hello, {athleteName}
          </h1>
          <p className="dashboard-date-subtitle">
            {todayFormatted} • {currentPlan?.phase_name || "Base Aerobic Phase"} (Revision #{currentPlan?.current_revision?.revision_number || 1})
          </p>
        </div>

        {activeEvent && (
          <div className="action-pill-group" onClick={() => onNavigateTab("plan")} title="View event details">
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
              {activeEvent.title} {eventDaysLeft !== null ? `(${eventDaysLeft}d to go)` : ""}
            </span>
            <span className="pill-icon-circle">→</span>
          </div>
        )}
      </div>

      {isRedFlagActive && (
        <div className="alert-banner alert-danger" style={{ marginBottom: "24px", padding: "18px 22px" }}>
          <div>
            <strong style={{ fontSize: "16px", display: "block", marginBottom: "4px" }}>
              URGENT MEDICAL SAFETY LOCKOUT ACTIVE
            </strong>
            <span style={{ fontSize: "13px", lineHeight: "1.5" }}>
              Red-flag symptoms were reported. All workout prescriptions and logging have been automatically suspended. Please consult a qualified physician before resuming exercise.
            </span>
          </div>
        </div>
      )}

      {/* Main Responsive Modular Dashboard Grid */}
      <div className="dashboard-grid">
        {/* =========================================================================
            COLUMN 1: Training Load & Volume Hero Widget + Readiness Card (Left)
           ========================================================================= */}
        <div className="col-span-4" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* Training Load / Volume Card (Reference Activities Card) */}
          <div className="highlight-hero-card">
            <div className="hero-glow" />
            <div style={{ position: "relative", zIndex: 2 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <strong style={{ fontSize: "15px", color: "#FFFFFF" }}>Training Volume</strong>
                </div>
                <span className="tag tag-espresso" style={{ fontSize: "10px", padding: "2px 8px" }}>
                  Week 1
                </span>
              </div>

              <div style={{ fontSize: "12px", color: "#ffcaa6", marginBottom: "14px" }}>
                Active microcycle in progress — on track with consistency
              </div>

              {/* Filter Pills */}
              <div style={{ display: "inline-flex", gap: "4px", background: "rgba(0,0,0,0.3)", padding: "3px", borderRadius: "var(--radius-full)", marginBottom: "14px" }}>
                {["week", "month", "all"].map((f) => (
                  <button
                    key={f}
                    type="button"
                    onClick={() => setTimeFilter(f)}
                    style={{
                      background: timeFilter === f ? "var(--accent-primary)" : "transparent",
                      color: timeFilter === f ? "#FFFFFF" : "var(--text-muted)",
                      border: "none",
                      borderRadius: "var(--radius-full)",
                      padding: "4px 12px",
                      fontSize: "11px",
                      fontWeight: 600,
                      cursor: "pointer",
                      textTransform: "capitalize",
                      transition: "all 0.15s ease",
                    }}
                  >
                    {f}
                  </button>
                ))}
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                <div>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                    Planned Volume
                  </span>
                  <div style={{ fontSize: "28px", fontWeight: 800, fontFamily: "var(--font-heading)", color: "#FFFFFF" }}>
                    {trends?.total_distance_km ? `${trends.total_distance_km} km` : "22.0 km"}
                  </div>
                </div>
                <span className="tag tag-orange" style={{ fontSize: "11px" }}>
                  {trends?.consistency_rate_pct ? `${trends.consistency_rate_pct}% Done` : "4 Sessions"}
                </span>
              </div>

              {/* 7-Day Mini Histogram Chart */}
              <div className="mini-histogram-grid">
                {miniBarData.map((bar, idx) => (
                  <div key={idx} className="mini-histogram-col">
                    <div className="mini-bar-track">
                      <div
                        className={`mini-bar-fill ${bar.isRest ? "rest" : ""} ${bar.isSessToday ? "today" : ""}`}
                        style={{ height: `${bar.heightPct}%` }}
                        title={`${bar.dayLabel}: ${bar.isRest ? "Rest" : `${bar.dist} km`}`}
                      />
                    </div>
                    <span className={`mini-col-label ${bar.isSessToday ? "today" : ""}`}>
                      {bar.isSessToday ? "Today" : bar.dayLabel}
                    </span>
                  </div>
                ))}
              </div>

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "10px 14px",
                  background: "rgba(0, 0, 0, 0.4)",
                  borderRadius: "var(--radius-md)",
                  border: "1px solid rgba(255, 255, 255, 0.08)",
                  marginTop: "6px",
                  fontSize: "12px",
                }}
              >
                <span style={{ color: "var(--text-secondary)" }}>
                  Today: <strong>{todaySession?.purpose || (todaySession?.session_type === "rest" ? "Active Recovery" : "Aerobic Run")}</strong>
                </span>
                <span style={{ color: "var(--accent-primary)", fontWeight: 700 }}>
                  {formatDist(todaySession)}
                </span>
              </div>
            </div>
          </div>

          {/* Readiness & Sleep Score Card (Reference Sleep / Readiness Card) */}
          <div className="card">
            <div className="card-header">
              <div>
                <h2 className="card-title">Recovery & Sleep Score</h2>
                <p className="card-subtitle">
                  {todayCheckIn ? "Logged for today" : "Not yet recorded today"}
                </p>
              </div>
              {todayCheckIn ? (
                <span className="tag tag-emerald">Completed</span>
              ) : (
                <button
                  type="button"
                  className="btn btn-primary btn-sm"
                  onClick={() => setShowCheckInModal(true)}
                >
                  Log Score
                </button>
              )}
            </div>

            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 0" }}>
              <div style={{ display: "flex", alignItems: "baseline", gap: "6px" }}>
                <span style={{ fontSize: "36px", fontWeight: 800, fontFamily: "var(--font-heading)", color: "var(--accent-primary)" }}>
                  {todayCheckIn ? readinessScore : "8.4"}
                </span>
                <span style={{ fontSize: "14px", color: "var(--text-muted)", fontWeight: 600 }}>/ 10</span>
              </div>
              <span className="tag tag-orange">
                {todayCheckIn ? (readinessScore >= 7.5 ? "Optimal State" : "Caution Tone") : "Good Readiness"}
              </span>
            </div>

            <div className="grid-3" style={{ marginTop: "6px" }}>
              <div className="stat-box" style={{ padding: "10px" }}>
                <div className="stat-value" style={{ fontSize: "18px" }}>{sleepVal}/5</div>
                <div className="stat-label" style={{ fontSize: "10px" }}>Sleep</div>
              </div>
              <div className="stat-box" style={{ padding: "10px" }}>
                <div className="stat-value" style={{ fontSize: "18px" }}>{sorenessVal}/5</div>
                <div className="stat-label" style={{ fontSize: "10px" }}>Soreness</div>
              </div>
              <div className="stat-box" style={{ padding: "10px" }}>
                <div className="stat-value" style={{ fontSize: "18px" }}>{energyVal}/5</div>
                <div className="stat-label" style={{ fontSize: "10px" }}>Energy</div>
              </div>
            </div>
          </div>
        </div>

        {/* =========================================================================
            COLUMN 2: Consistency Gauge + Fatigue Arc + Hydration/Nutrition (Center)
           ========================================================================= */}
        <div className="col-span-4" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* Consistency & Fatigue Widgets Row */}
          <div className="grid-2" style={{ gap: "16px" }}>
            {/* Circular Gauge 1: Consistency */}
            <div className="card" style={{ padding: "18px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                <strong style={{ fontSize: "13px", color: "var(--text-primary)" }}>Adherence</strong>
                <span style={{ fontSize: "12px", color: "var(--accent-primary)" }}>↗</span>
              </div>

              <div className="gauge-widget-container">
                <svg className="gauge-svg-circle" viewBox="0 0 36 36">
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="rgba(255, 255, 255, 0.08)"
                    strokeWidth="3.5"
                  />
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="var(--accent-primary)"
                    strokeWidth="3.5"
                    strokeDasharray={`${trends?.consistency_rate_pct || 85}, 100`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="gauge-center-text">
                  <div className="gauge-center-value">{trends?.total_runs_completed || 1}</div>
                  <div className="gauge-center-label">Runs Done</div>
                </div>
              </div>
            </div>

            {/* Semicircular Arc Gauge 2: Stress / Tone */}
            <div className="card" style={{ padding: "18px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                <strong style={{ fontSize: "13px", color: "var(--text-primary)" }}>Stress</strong>
                <span style={{ fontSize: "12px", color: "var(--accent-cyan)" }}>↗</span>
              </div>

              <div className="gauge-widget-container">
                <div style={{ fontSize: "28px", fontWeight: 800, fontFamily: "var(--font-heading)", color: "var(--text-primary)", marginTop: "10px" }}>
                  {stressVal <= 2 ? "Low" : stressVal === 3 ? "Moderate" : "High"}
                </div>
                <div style={{ width: "100%", height: "8px", background: "rgba(255,255,255,0.08)", borderRadius: "var(--radius-full)", overflow: "hidden", marginTop: "14px" }}>
                  <div
                    style={{
                      height: "100%",
                      width: `${(stressVal / 5) * 100}%`,
                      background: stressVal <= 2 ? "var(--accent-emerald)" : stressVal === 3 ? "var(--accent-amber)" : "var(--accent-crimson)",
                      borderRadius: "var(--radius-full)",
                    }}
                  />
                </div>
                <div className="gauge-center-label" style={{ marginTop: "10px" }}>
                  {stressVal <= 2 ? "Optimal Tone" : "Tension Monitored"}
                </div>
              </div>
            </div>
          </div>

          {/* Hydration Widget (Reference Water Widget) */}
          <div className="card" style={{ padding: "18px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <strong style={{ fontSize: "14px", color: "var(--text-primary)" }}>Hydration Target</strong>
              </div>
              <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--accent-cyan)" }}>
                {todayNutrition?.hydration_liters || "2.8"} Liters
              </span>
            </div>

            <div className="water-level-bar-container">
              {[40, 65, 85, 100, 75, 50, 90, 100, 60, 45].map((h, i) => (
                <div
                  key={i}
                  className={`water-stick ${i < 7 ? "active" : ""}`}
                  style={{ height: `${h}%` }}
                />
              ))}
            </div>
            <p style={{ fontSize: "11px", color: "var(--text-muted)" }}>
              Baseline sports hydration requirement for Indian climate & sweat rate
            </p>
          </div>

          {/* Fuel & Nutrition Macro Target Summary */}
          <div className="card" style={{ padding: "18px" }}>
            <div className="card-header" style={{ marginBottom: "12px" }}>
              <div>
                <strong style={{ fontSize: "14px", color: "var(--text-primary)" }}>Fuel & Calorie Blueprint</strong>
                <p style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                  {todayNutrition?.diet_type?.replace("_", " ") || "Vegetarian"} ({todayNutrition?.region?.replace("_", " ") || "North Indian"})
                </p>
              </div>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                style={{ padding: "3px 10px", fontSize: "11px" }}
                onClick={() => onNavigateTab("nutrition")}
              >
                Details →
              </button>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "12px" }}>
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Carbohydrates</span>
                  <strong style={{ color: "var(--accent-cyan)" }}>
                    {todayNutrition?.carbs_g_min && todayNutrition?.carbs_g_max ? `${todayNutrition.carbs_g_min}–${todayNutrition.carbs_g_max}g` : "230–310g"}
                  </strong>
                </div>
                <div style={{ height: "6px", background: "rgba(255,255,255,0.06)", borderRadius: "var(--radius-full)", overflow: "hidden" }}>
                  <div style={{ width: "78%", height: "100%", background: "var(--accent-cyan)", borderRadius: "var(--radius-full)" }} />
                </div>
              </div>

              <div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                  <span style={{ color: "var(--text-secondary)" }}>Protein</span>
                  <strong style={{ color: "var(--accent-primary)" }}>
                    {todayNutrition?.protein_g_min && todayNutrition?.protein_g_max ? `${todayNutrition.protein_g_min}–${todayNutrition.protein_g_max}g` : "80–105g"}
                  </strong>
                </div>
                <div style={{ height: "6px", background: "rgba(255,255,255,0.06)", borderRadius: "var(--radius-full)", overflow: "hidden" }}>
                  <div style={{ width: "85%", height: "100%", background: "var(--accent-primary)", borderRadius: "var(--radius-full)" }} />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* =========================================================================
            COLUMN 3: Prominent Workout Action Hero Card (Right)
           ========================================================================= */}
        <div className="col-span-4" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* Prominent Workout Hero Card (Reference Prominent Right Card) */}
          <div className="workout-feature-card">
            <div className="card-header" style={{ marginBottom: "12px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span className="tag tag-orange">
                  {todaySession?.session_type?.replace("_", " ") || "Running"}
                </span>
                <span className="tag tag-espresso">Today</span>
              </div>
            </div>

            <div style={{ marginBottom: "16px" }}>
              <h2 style={{ fontSize: "20px", fontWeight: 800, color: "var(--text-primary)", marginBottom: "4px" }}>
                {todaySession?.purpose || todaySession?.title || (todaySession?.session_type === "rest" ? "Active Recovery" : "Training Session")}
              </h2>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.5" }}>
                {todaySession?.effort_target || (todaySession?.session_type === "rest" ? "Prioritize sleep and hydration recovery." : "Aerobic base building session.")}
              </p>
            </div>

            <div style={{ display: "flex", alignItems: "baseline", gap: "8px", margin: "16px 0" }}>
              <span style={{ fontSize: "40px", fontWeight: 800, fontFamily: "var(--font-heading)", color: "#FFFFFF" }}>
                {formatDist(todaySession)}
              </span>
              <span style={{ fontSize: "14px", color: "var(--text-muted)", fontWeight: 600 }}>
                • {formatDur(todaySession)}
              </span>
            </div>

            {/* Session Stats Grid */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", padding: "12px", background: "rgba(0,0,0,0.35)", borderRadius: "var(--radius-md)", marginBottom: "20px" }}>
              <div>
                <span style={{ fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase" }}>Target Pace</span>
                <div style={{ fontSize: "14px", fontWeight: 700, color: "var(--accent-cyan)", marginTop: "2px" }}>
                  {formatPace(todaySession?.target_pace_sec_per_km)}
                </div>
              </div>
              <div>
                <span style={{ fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase" }}>Priority</span>
                <div style={{ fontSize: "14px", fontWeight: 700, color: todaySession?.priority === "high" ? "var(--accent-amber)" : "var(--text-primary)", marginTop: "2px" }}>
                  {todaySession?.priority === "high" ? "Key Session" : "Standard"}
                </div>
              </div>
            </div>

            {/* CTA Buttons */}
            {isRedFlagActive ? (
              <div className="alert-banner alert-danger" style={{ marginBottom: 0, padding: "12px" }}>
                Locked: Medical clearance required.
              </div>
            ) : todaySession?.session_type !== "rest" ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                <button
                  type="button"
                  className="btn btn-primary btn-lg"
                  style={{ width: "100%" }}
                  onClick={() => onNavigateTab("train")}
                >
                  Start Live Workout →
                </button>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  style={{ width: "100%" }}
                  onClick={() => onNavigateTab("train")}
                >
                  Log Completed Manually
                </button>
              </div>
            ) : (
              <div className="alert-banner alert-info" style={{ marginBottom: 0, padding: "14px" }}>
                Rest Day: Complete rest for recovery.
              </div>
            )}
          </div>

          {/* Coaching Engine Rationale Mini Card */}
          <div className="card" style={{ padding: "18px" }}>
            <div className="card-header" style={{ marginBottom: "8px" }}>
              <strong style={{ fontSize: "13px", color: "var(--text-primary)" }}>Coaching Engine Rationale</strong>
              <span className="tag tag-orange" style={{ fontSize: "9px" }}>Deterministic</span>
            </div>
            <p style={{ fontSize: "12px", color: "var(--text-secondary)", lineHeight: "1.5" }}>
              {currentPlan?.current_revision?.explanation ||
                currentPlan?.coach_reasoning ||
                "This 7-day microcycle safely balances volume progression with structured recovery to build aerobic capacity without injury spikes."}
            </p>
          </div>
        </div>

        {/* =========================================================================
            ROW 2: 7-Day Rolling Microcycle Schedule Strip (Full Width)
           ========================================================================= */}
        <div className="col-span-12">
          <div className="card">
            <div className="card-header">
              <div>
                <h2 className="card-title">7-Day Rolling Microcycle Schedule</h2>
                <p className="card-subtitle">Upcoming sessions and active recovery distribution</p>
              </div>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => onNavigateTab("plan")}
              >
                View Full Plan & Revisions →
              </button>
            </div>

            {sessions.length === 0 ? (
              <p className="muted" style={{ padding: "20px 0", textAlign: "center" }}>
                No scheduled sessions found for current microcycle.
              </p>
            ) : (
              <div className="microcycle-strip">
                {sessions.map((s, idx) => {
                  const dateStr = s.local_date || s.scheduled_date || "";
                  const isSessToday = dateStr === todayStr;
                  const isRest = s.session_type === "rest";
                  const dateObj = new Date(dateStr + "T00:00:00");
                  const weekdayShort = isNaN(dateObj.getTime()) ? "DAY" : dateObj.toLocaleDateString("en-US", { weekday: "short" });
                  const dayNum = isNaN(dateObj.getTime()) ? dateStr.slice(-2) : dateObj.getDate();

                  return (
                    <div
                      key={s.id || idx}
                      className={`microcycle-day-card ${isSessToday ? "today" : ""}`}
                      onClick={() => onNavigateTab("plan")}
                      style={{ cursor: "pointer" }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                        <span style={{ fontSize: "11px", fontWeight: 700, color: isSessToday ? "var(--accent-primary)" : "var(--text-muted)", textTransform: "uppercase" }}>
                          {weekdayShort} {dayNum}
                        </span>
                        {isSessToday && <span className="tag tag-orange" style={{ padding: "1px 6px", fontSize: "9px" }}>Today</span>}
                      </div>

                      <strong style={{ fontSize: "13px", color: "var(--text-primary)", display: "block", marginBottom: "4px" }}>
                        {isRest ? "Active Rest" : s.session_type?.replace("_", " ")}
                      </strong>

                      <div style={{ fontSize: "12px", color: isRest ? "var(--text-muted)" : "var(--accent-primary)", fontWeight: 600 }}>
                        {isRest ? "Recovery" : formatDist(s)}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Check-In Modal */}
      <CheckInModal
        isOpen={showCheckInModal}
        onClose={() => setShowCheckInModal(false)}
        initialData={todayCheckIn}
        onCheckInRecorded={() => {
          if (onRefreshData) onRefreshData();
        }}
      />
    </div>
  );
}
