import React, { useState, useEffect, useRef } from "react";
import { logActivity } from "../api.js";
import DisclaimerBanner from "../components/DisclaimerBanner.jsx";

export default function Train({ currentPlan, todayCheckIn, activeEvent, onWorkoutLogged, onNavigateTab }) {
  const todayStr = new Date().toISOString().slice(0, 10);
  const sessions = currentPlan?.sessions || [];
  const todaySession =
    sessions.find((s) => (s.local_date || s.scheduled_date) === todayStr) ||
    sessions[0] ||
    null;
  const activityType = activeEvent?.sport || "running";
  const distanceUnit = activityType === "swimming" ? "m" : activityType === "running" || activityType === "cycling" ? "km" : "";

  // Red-Flag Safety Lockout
  const isRedFlagActive = Boolean(
    todayCheckIn?.red_flag_symptom ||
    currentPlan?.current_revision?.explanation?.includes("URGENT SAFETY STOP") ||
    currentPlan?.current_revision?.trigger_reason === "RED_FLAG_SAFETY_STOP"
  );

  // Stopwatch state
  const [timerRunning, setTimerRunning] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const timerRef = useRef(null);

  // Form / completion state
  const initialDist = todaySession?.distance_km_max || todaySession?.distance_km_min || todaySession?.planned_distance_km || 5.0;
  const initialDur = todaySession?.duration_min_max || todaySession?.duration_min_min || todaySession?.planned_duration_minutes || 30;

  const [completedDist, setCompletedDist] = useState(initialDist);
  const [rpe, setRpe] = useState(5);
  const [effortNotes, setEffortNotes] = useState("");
  const [stoppedEarly, setStoppedEarly] = useState(false);
  const [earlyStopReason, setEarlyStopReason] = useState("");

  const [hasPain, setHasPain] = useState(false);
  const [painLocation, setPainLocation] = useState("");
  const [painSeverity, setPainSeverity] = useState(3);

  const [loading, setLoading] = useState(false);
  const [successResult, setSuccessResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (timerRunning) {
      timerRef.current = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [timerRunning]);

  function formatTimer(seconds) {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hrs > 0) {
      return `${hrs.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    }
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  }

  function handleEarlyStop() {
    setTimerRunning(false);
    setStoppedEarly(true);
    setHasPain(true);
  }

  async function handleLogActivity(e) {
    e.preventDefault();
    if (isRedFlagActive) {
      setError("Training is currently suspended due to reported red-flag medical symptoms. Please seek physician evaluation.");
      return;
    }
    setLoading(true);
    setError("");

    try {
      const durationMin = elapsedSeconds > 0
        ? Number((elapsedSeconds / 60).toFixed(1))
        : Number(initialDur);

      const payload = {
        planned_session_id: todaySession?.id || null,
        local_date: todayStr,
        activity_type: activityType,
        duration_min: durationMin,
        distance_km: distanceUnit === "km" && completedDist !== "" ? Number(completedDist) : null,
        perceived_effort: Number(rpe),
        completion_state: stoppedEarly ? "partial" : "completed",
        early_stop_reason: stoppedEarly ? earlyStopReason : "",
        pain_flag: Boolean(hasPain),
        pain_notes: hasPain ? `${painLocation} (severity ${painSeverity}/10)` : "",
        notes: effortNotes.trim() || "",
      };

      const result = await logActivity(payload);
      setSuccessResult(result);
      if (onWorkoutLogged) onWorkoutLogged(result);
    } catch (err) {
      setError(err.message || "Failed to log completed activity.");
    } finally {
      setLoading(false);
    }
  }

  // Parse workout blocks if present
  let workoutBlocks = [];
  if (todaySession?.blocks_json) {
    try {
      const parsed = JSON.parse(todaySession.blocks_json);
      if (Array.isArray(parsed)) workoutBlocks = parsed;
    } catch {
      // Ignore
    }
  }

  return (
    <div>
      <DisclaimerBanner type="general" />

      {isRedFlagActive ? (
        <div className="card" style={{ border: "2px solid var(--accent-crimson)", background: "rgba(239, 68, 68, 0.08)", padding: "36px 24px", textAlign: "center" }}>
          <h2 style={{ fontSize: "24px", color: "var(--accent-crimson)", marginBottom: "12px" }}>
            URGENT SAFETY STOP: Medical Clearance Required
          </h2>
          <p style={{ color: "#fca5a5", fontSize: "15px", maxWidth: "620px", margin: "0 auto 20px auto", lineHeight: "1.6" }}>
            Red-flag symptoms (chest pain, dizziness, severe breathlessness, or acute musculoskeletal trauma) have been reported. All workout recommendations and execution are strictly suspended.
          </p>
          <div style={{ background: "rgba(0,0,0,0.4)", borderRadius: "var(--radius-md)", padding: "18px", maxWidth: "600px", margin: "0 auto 24px auto", textAlign: "left" }}>
            <strong style={{ color: "var(--text-primary)", display: "block", marginBottom: "8px" }}>
              Immediate Athlete Instructions:
            </strong>
            <ul style={{ paddingLeft: "20px", fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.6" }}>
              <li>Do not perform any high-intensity, running, or strenuous physical activity.</li>
              <li>Seek prompt clinical evaluation from a qualified sports physician or emergency care provider.</li>
              <li>There is no bypass or manual override for this safety lockout.</li>
            </ul>
          </div>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => onNavigateTab("home")}
          >
            ← Return to Home
          </button>
        </div>
      ) : successResult ? (
        <div className="card" style={{ textAlign: "center", padding: "40px 24px" }}>
          <h2 style={{ fontSize: "24px", color: "var(--accent-primary)", marginBottom: "8px" }}>
            Workout Logged Successfully
          </h2>
          <p style={{ color: "var(--text-secondary)", maxWidth: "480px", margin: "0 auto 24px auto" }}>
            Great effort. Your training metrics have been saved to your immutable performance log.
          </p>

          {successResult.adaptations && successResult.adaptations.length > 0 && (
            <div
              style={{
                maxWidth: "600px",
                margin: "0 auto 24px auto",
                padding: "16px",
                borderRadius: "var(--radius-md)",
                background: "var(--accent-cyan-dim)",
                border: "1px solid rgba(56, 189, 248, 0.3)",
                textAlign: "left",
              }}
            >
              <strong style={{ color: "var(--accent-cyan)", display: "block", marginBottom: "6px" }}>
                Coach Engine Applied Adaptations:
              </strong>
              <ul style={{ paddingLeft: "20px", fontSize: "13px", color: "#e0f2fe" }}>
                {successResult.adaptations.map((a, i) => (
                  <li key={i}>{a.reasoning || a.action_type}</li>
                ))}
              </ul>
            </div>
          )}

          <div style={{ display: "flex", justifyContent: "center", gap: "12px" }}>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => onNavigateTab("home")}
            >
              Back to Home
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => onNavigateTab("progress")}
            >
              View Progress Trends →
            </button>
          </div>
        </div>
      ) : (
        <div className="grid-2">
          {/* Left Column: Live Workout Execution Timer */}
          <div className="card">
            <div className="card-header">
              <div>
                <h2 className="card-title">Live Workout Session</h2>
                <p className="card-subtitle">
                  {todaySession?.purpose || todaySession?.title || "Scheduled Training Session"}
                </p>
              </div>
              <span className="tag tag-orange">Interactive Stopwatch</span>
            </div>

            <div className="workout-block-item" style={{ marginBottom: "14px" }}>
              <div><strong>Session target</strong><p className="muted">{todaySession?.purpose || "No session is scheduled in this 7-day window."}</p></div>
              {todaySession?.effort_target && <span className="tag tag-cyan">{todaySession.effort_target}</span>}
            </div>

            <div className="timer-display">{formatTimer(elapsedSeconds)}</div>

            <div style={{ display: "flex", justifyContent: "center", gap: "12px", marginBottom: "24px", flexWrap: "wrap" }}>
              {!timerRunning ? (
                <button
                  type="button"
                  className="btn btn-primary btn-lg"
                  onClick={() => setTimerRunning(true)}
                >
                  Start Workout
                </button>
              ) : (
                <button
                  type="button"
                  className="btn btn-secondary btn-lg"
                  onClick={() => setTimerRunning(false)}
                >
                  Pause
                </button>
              )}

              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  setTimerRunning(false);
                  setElapsedSeconds(0);
                }}
              >
                Reset
              </button>

              <button
                type="button"
                className="btn btn-danger btn-sm"
                onClick={handleEarlyStop}
                title="Stop workout early due to discomfort or fatigue"
              >
                Stop Early
              </button>
            </div>

            {/* Session Guidance Blocks */}
            <div style={{ marginTop: "20px" }}>
              <h3 style={{ fontSize: "12px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "10px" }}>
                Target Session Structure
              </h3>

              {workoutBlocks.length > 0 ? (
                workoutBlocks.map((b, i) => (
                  <div key={i} className="workout-block-item">
                    <div>
                      <strong style={{ fontSize: "14px", color: "var(--text-primary)", textTransform: "capitalize" }}>
                        {b.name?.replace("_", " ") || `Block ${i + 1}`}
                      </strong>
                      <p style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                        {b.description}
                      </p>
                    </div>
                    {b.duration_min && <span className="tag tag-neutral">{b.duration_min} min</span>}
                  </div>
                ))
              ) : (
                <>
                  <div className="workout-block-item">
                    <div>
                      <strong style={{ fontSize: "14px", color: "var(--text-primary)" }}>1. Warmup & Mobility</strong>
                      <p style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                        10 mins very easy conversational jog + dynamic leg swings
                      </p>
                    </div>
                    <span className="tag tag-neutral">RPE 2-3</span>
                  </div>

                  <div className="workout-block-item" style={{ borderLeft: "3px solid var(--accent-primary)" }}>
                    <div>
                      <strong style={{ fontSize: "14px", color: "var(--accent-primary)" }}>
                        2. Main Block: {todaySession?.purpose || "Aerobic Build"}
                      </strong>
                      <p style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                        {todaySession?.effort_target || "Steady aerobic target pace"}
                      </p>
                    </div>
                    <span className="tag tag-orange">RPE 4-5</span>
                  </div>

                  <div className="workout-block-item">
                    <div>
                      <strong style={{ fontSize: "14px", color: "var(--text-primary)" }}>3. Cooldown & Hydration</strong>
                      <p style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                        5 mins gentle walk + calf/quad stretches
                      </p>
                    </div>
                    <span className="tag tag-neutral">RPE 1-2</span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Right Column: Complete & Log Activity Form */}
          <div className="card">
            <div className="card-header">
              <div>
                <h2 className="card-title">Log Completed Activity</h2>
                <p className="card-subtitle">Record actual distance, time, and perceived effort</p>
              </div>
            </div>

            {error && <div className="alert-banner alert-danger">{error}</div>}

            <form onSubmit={handleLogActivity}>
              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">Completed Distance {distanceUnit ? `(${distanceUnit})` : "(optional)"}</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    className="form-input"
                    value={completedDist}
                    onChange={(e) => setCompletedDist(e.target.value)}
                    required={distanceUnit === "km"}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Duration (Minutes / Stopwatch)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="1"
                    className="form-input"
                    value={
                      elapsedSeconds > 0
                        ? (elapsedSeconds / 60).toFixed(1)
                        : initialDur
                    }
                    onChange={(e) => setElapsedSeconds(Math.round(Number(e.target.value) * 60))}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">
                  Rate of Perceived Exertion (RPE 1-10 Slider)
                </label>
                <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    className="form-input"
                    style={{ flex: 1 }}
                    value={rpe}
                    onChange={(e) => setRpe(e.target.value)}
                  />
                  <span className="stat-value" style={{ fontSize: "22px", width: "40px", textAlign: "center", color: rpe >= 8 ? "var(--accent-amber)" : "var(--accent-primary)" }}>
                    {rpe}
                  </span>
                </div>
                <p style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
                  {rpe <= 3 && "Very light conversational pace"}
                  {rpe >= 4 && rpe <= 6 && "Moderate aerobic effort (Zone 2-3)"}
                  {rpe >= 7 && rpe <= 8 && "Hard threshold / tempo effort"}
                  {rpe >= 9 && "Maximum / all-out effort (May trigger recovery adaptation)"}
                </p>
              </div>

              {stoppedEarly && (
                <div style={{ padding: "14px", background: "var(--accent-amber-dim)", border: "1px solid rgba(251, 191, 36, 0.3)", borderRadius: "var(--radius-md)", marginBottom: "16px" }}>
                  <label className="form-label" style={{ color: "var(--accent-amber)" }}>
                    Reason for Stopping Early *
                  </label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Sharp pain in right calf, extreme sudden dizziness"
                    value={earlyStopReason}
                    onChange={(e) => setEarlyStopReason(e.target.value)}
                    required={stoppedEarly}
                  />
                </div>
              )}

              <div style={{ padding: "14px", background: "rgba(0,0,0,0.25)", borderRadius: "var(--radius-md)", marginBottom: "16px" }}>
                <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer", fontWeight: 600, fontSize: "13px" }}>
                  <input
                    type="checkbox"
                    checked={hasPain}
                    onChange={(e) => setHasPain(e.target.checked)}
                    style={{ width: "16px", height: "16px", accentColor: "var(--accent-amber)" }}
                  />
                  <span>Report Pain or Musculoskeletal Discomfort during session</span>
                </label>

                {hasPain && (
                  <div className="grid-2" style={{ marginTop: "12px" }}>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                      <label className="form-label">Pain Location</label>
                      <input
                        type="text"
                        className="form-input"
                        placeholder="e.g. Left Knee, Shin"
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

              <div className="form-group">
                <label className="form-label">Session Notes / Feeling</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Felt strong in the middle kilometers, humid morning"
                  value={effortNotes}
                  onChange={(e) => setEffortNotes(e.target.value)}
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                style={{ width: "100%", marginTop: "10px" }}
                disabled={loading}
              >
                {loading ? "Saving Activity..." : "Log Activity & Check Adaptations →"}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
