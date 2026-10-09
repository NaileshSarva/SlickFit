import React, { useState } from "react";
import DisclaimerBanner from "../components/DisclaimerBanner.jsx";

/**
 * Nutrition view.
 * API shape (from /nutrition/today):
 *   dietary_pattern, regional_preference, min_kcal, max_kcal,
 *   protein_g_min, protein_g_max, carbs_g_min, carbs_g_max,
 *   fats_g_min, fats_g_max, hydration_liters,
 *   meal_ideas[{meal, idea, protein_source}], rationale, limitations
 */
export default function Nutrition({ todayNutrition, user }) {
  const n = todayNutrition || null;
  const [checkedMeals, setCheckedMeals] = useState({});

  // Readable labels — explicit null check prevents rendering empty parentheses.
  const rawDiet = n?.dietary_pattern;
  const rawRegion = n?.regional_preference;
  const dietLabel = rawDiet ? rawDiet.replace(/_/g, " ") : null;
  const regionLabel = rawRegion ? rawRegion.replace(/_/g, " ") : null;

  // meal_ideas from the API
  const mealIdeas = Array.isArray(n?.meal_ideas) ? n.meal_ideas : [];


  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      <DisclaimerBanner type="nutrition" />

      {/* Hero Targets Banner */}
      <div className="highlight-hero-card">
        <div className="hero-glow" />
        <div style={{ position: "relative", zIndex: 2 }}>
          <div className="card-header" style={{ marginBottom: "12px" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                <span className="tag tag-orange">General guidance</span>
                {regionLabel && <span className="tag tag-espresso">{regionLabel}</span>}
              </div>
              <h1 style={{ fontSize: "24px", fontWeight: 800 }}>
                Daily Athletic Fuel &amp; Hydration Blueprint
              </h1>
              <p style={{ color: "var(--text-secondary)", fontSize: "13px", marginTop: "4px" }}>
                {dietLabel && regionLabel ? (
                  <>
                    Tailored for:{" "}
                    <strong style={{ color: "var(--text-primary)" }}>{dietLabel}</strong>{" "}
                    ({regionLabel})
                  </>
                ) : dietLabel ? (
                  <>
                    Diet type:{" "}
                    <strong style={{ color: "var(--text-primary)" }}>{dietLabel}</strong>
                  </>
                ) : (
                  <span style={{ color: "var(--text-muted)" }}>
                    Diet and region not set — targets below are general guidance only.
                  </span>
                )}
              </p>
              {n?.rationale && (
                <p style={{ color: "var(--text-muted)", fontSize: "12px", marginTop: "4px" }}>
                  {n.rationale}
                </p>
              )}
            </div>
          </div>

          <div className="grid-3" style={{ marginTop: "14px" }}>
            <div className="stat-box">
              <div className="stat-value" style={{ color: "var(--accent-cyan)", fontSize: "24px" }}>
                {n?.carbs_g_min && n?.carbs_g_max
                  ? `${n.carbs_g_min}–${n.carbs_g_max} g`
                  : "--"}
              </div>
              <div className="stat-label">Carbohydrate Target</div>
              <p style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
                {n?.carbs_g_min ? "Glycogen replenishment range" : "Log a session to get a target"}
              </p>
            </div>

            <div className="stat-box">
              <div className="stat-value" style={{ color: "var(--accent-primary)", fontSize: "24px" }}>
                {n?.protein_g_min != null && n?.protein_g_max != null
                  ? `${n.protein_g_min}–${n.protein_g_max} g`
                  : "--"}
              </div>
              <div className="stat-label">Daily Protein Target</div>
              <p style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
                {n?.protein_g_min ? "Distributed for muscular recovery" : "Log a session to get a target"}
              </p>
            </div>

            <div className="stat-box">
              <div className="stat-value" style={{ color: "var(--accent-amber)", fontSize: "24px" }}>
                {n?.min_kcal != null && n?.max_kcal != null
                  ? `${n.min_kcal}–${n.max_kcal} kcal`
                  : "--"}
              </div>
              <div className="stat-label">Estimated Energy</div>
              <p style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "4px" }}>
                {n?.hydration_liters
                  ? `Hydration: ${n.hydration_liters}L / day`
                  : "Hydration estimate unavailable"}
              </p>
            </div>
          </div>
        </div>
      </div>

      {n && <div className="card">
        <div className="card-header"><div><h2 className="card-title">Today’s context</h2><p className="card-subtitle">Guidance uses the current planned session and saved food preferences.</p></div><span className="tag tag-cyan">{n.local_date}</span></div>
        <p className="muted">{n.rationale}</p>
        {user?.profile?.weight_kg == null && <p className="muted" style={{ marginTop: "8px" }}>No body weight is on file, so the nutrition estimate uses a generic reference value. Add or correct your weight in Profile to personalize weight-based ranges.</p>}
      </div>}
      {n && <div className="card">
        <div className="card-header"><div><h2 className="card-title">Personal fueling range</h2><p className="card-subtitle">Ranges are broad estimates, not a prescription.</p></div></div>
        <div className="grid-2">
          <div><strong>Fat</strong><p className="muted">{n.fats_g_min}–{n.fats_g_max} g/day</p></div>
          <div><strong>Hydration estimate</strong><p className="muted">{n.hydration_liters} L/day reference</p></div>
        </div>
      </div>}

      {/* Today's Meal Ideas — API generated and preference-filtered suggestions */}
      <div className="card">
        <div className="card-header" style={{ marginBottom: "14px" }}>
          <div>
            <h2 className="card-title">Today's Meal Ideas</h2>
            <p className="card-subtitle">
              {mealIdeas.length > 0
                ? "Suggested meals based on your training day and preferences"
                : "What and when to eat around your scheduled workout"}
            </p>
          </div>
        </div>

        {mealIdeas.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {mealIdeas.map((m, idx) => (
              <div
                key={idx}
                style={{
                  padding: "14px 16px",
                  borderRadius: "var(--radius-md)",
                  background: "rgba(0,0,0,0.3)",
                  border: "1px solid var(--border-subtle)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px", flexWrap: "wrap", gap: "6px" }}>
                  <strong style={{ fontSize: "14px", color: "var(--accent-primary)" }}>
                    {m.meal}
                  </strong>
                  {m.protein_source && (
                    <span className="tag tag-cyan" style={{ fontSize: "10px", padding: "2px 8px" }}>
                      {m.protein_source}
                    </span>
                  )}
                </div>
                <p style={{ fontSize: "13px", color: "var(--text-primary)", lineHeight: "1.4" }}>
                  {m.idea}
                </p>
                <label style={{ display: "flex", gap: "8px", alignItems: "center", marginTop: "10px", color: "var(--text-muted)", fontSize: "12px" }}>
                  <input type="checkbox" checked={Boolean(checkedMeals[idx])} onChange={(e) => setCheckedMeals((old) => ({ ...old, [idx]: e.target.checked }))} /> Mark as considered
                </label>
              </div>
            ))}
          </div>
        ) : (
          <div
            style={{
              padding: "24px 16px",
              borderRadius: "var(--radius-md)",
              background: "rgba(0,0,0,0.2)",
              border: "1px solid var(--border-subtle)",
              textAlign: "center",
              color: "var(--text-muted)",
              fontSize: "13px",
            }}
          >
            <strong style={{ display: "block", marginBottom: "4px", color: "var(--text-secondary)" }}>
              No meal ideas yet
            </strong>
            <p>
              Meal suggestions appear once your daily plan has been generated.
              Complete onboarding and set a target event to get started.
            </p>
          </div>
        )}
      </div>

      {/* Limitations notice when present */}
      {n?.limitations && (
        <p style={{ fontSize: "11px", color: "var(--text-dim)", textAlign: "center", lineHeight: "1.5" }}>
          {n.limitations}
        </p>
      )}
    </div>
  );
}
