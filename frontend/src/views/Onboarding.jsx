import React, { useState } from "react";
import { submitOnboarding } from "../api.js";
import DisclaimerBanner from "../components/DisclaimerBanner.jsx";

export default function Onboarding({ onOnboardingComplete }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Step 1: Target Event
  const [eventTitle, setEventTitle] = useState("Airtel Delhi Half Marathon");
  const [sportType, setSportType] = useState("running");
  const [targetDistanceKm, setTargetDistanceKm] = useState(21.1);
  const [targetDate, setTargetDate] = useState(
    new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
  );
  const [targetTimeGoal, setTargetTimeGoal] = useState("1:55:00");

  // Step 2: Baseline Assessment
  const [hasNoBaseline, setHasNoBaseline] = useState(false);
  const [weeklyVolumeKm, setWeeklyVolumeKm] = useState(20);
  const [recentRaceDistKm, setRecentRaceDistKm] = useState(10);
  const [recentRaceTimeMin, setRecentRaceTimeMin] = useState(54);
  const [easyPaceMinKm, setEasyPaceMinKm] = useState(6.2);

  // Step 3: Availability & Time Caps
  const [availableDays, setAvailableDays] = useState(["tuesday", "thursday", "saturday", "sunday"]);
  const [longRunDay, setLongRunDay] = useState("sunday");
  const [maxWeekdayMin, setMaxWeekdayMin] = useState(60);
  const [maxWeekendMin, setMaxWeekendMin] = useState(120);

  // Step 4: Profile & Safety Screening
  const [displayName, setDisplayName] = useState("");
  const [ageBand, setAgeBand] = useState("");
  const [region, setRegion] = useState("");
  const [hasChestPain, setHasChestPain] = useState(false);
  const [hasDizziness, setHasDizziness] = useState(false);
  const [hasJointPain, setHasJointPain] = useState(false);

  // Step 5: Nutrition & Allergies
  const [dietType, setDietType] = useState("vegetarian");
  const [dietRegion, setDietRegion] = useState("north_indian");
  const [allergies, setAllergies] = useState([]);

  function toggleDay(day) {
    if (availableDays.includes(day)) {
      if (availableDays.length <= 2) {
        setError("Please select at least 2 available training days per week.");
        return;
      }
      setAvailableDays(availableDays.filter((d) => d !== day));
    } else {
      setAvailableDays([...availableDays, day]);
    }
  }

  function toggleAllergy(allergy) {
    if (allergies.includes(allergy)) {
      setAllergies(allergies.filter((a) => a !== allergy));
    } else {
      setAllergies([...allergies, allergy]);
    }
  }

  async function handleComplete(e) {
    if (e) e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const payload = {
        event: {
          kind: sportType === "custom" ? "custom" : "running",
          sport: sportType === "custom" ? "custom" : "running",
          title: eventTitle.trim() || "Target Endurance Event",
          event_date: targetDate,
          goal_type: "finish",
          target_value: sportType === "running" ? (Number(targetDistanceKm) || 10.0) : null,
          target_unit: "km",
          notes: targetTimeGoal.trim() || "",
        },
        baseline: {
          experience_level: "beginner",
          recent_weekly_km: hasNoBaseline ? null : (Number(weeklyVolumeKm) || null),
          recent_runs_per_week: hasNoBaseline ? null : availableDays.length,
          recent_race_distance_km: hasNoBaseline ? null : (Number(recentRaceDistKm) || null),
          recent_race_time_sec:
            hasNoBaseline || !recentRaceTimeMin ? null : Math.round(Number(recentRaceTimeMin) * 60),
          easy_pace_sec_per_km:
            hasNoBaseline || !easyPaceMinKm ? null : Math.round(Number(easyPaceMinKm) * 60),
        },
        availability: {
          training_days: availableDays,
          daily_time_cap_min: Number(maxWeekdayMin) || 60,
          preferred_times: ["morning"],
          environment_equipment: "road_outdoor",
        },
        profile: {
          age_band: ageBand.trim() || null,
          region: region.trim() || null,
        },
        nutrition: {
          dietary_pattern: dietType,
          regional_preference: dietRegion,
          allergies: allergies,
        },
      };

      const result = await submitOnboarding(payload);
      if (onOnboardingComplete) {
        onOnboardingComplete(result);
      }
    } catch (err) {
      setError(err.message || "Failed to generate initial plan. Please check inputs.");
    } finally {
      setLoading(false);
    }
  }

  const daysList = [
    { key: "monday", label: "Mon" },
    { key: "tuesday", label: "Tue" },
    { key: "wednesday", label: "Wed" },
    { key: "thursday", label: "Thu" },
    { key: "friday", label: "Fri" },
    { key: "saturday", label: "Sat" },
    { key: "sunday", label: "Sun" },
  ];

  const commonAllergies = [
    { key: "peanuts", label: "Peanuts / Groundnuts" },
    { key: "tree_nuts", label: "Tree Nuts (Almonds/Cashews)" },
    { key: "dairy", label: "Dairy / Lactose" },
    { key: "gluten", label: "Gluten / Wheat" },
    { key: "soy", label: "Soy" },
    { key: "eggs", label: "Eggs" },
    { key: "shellfish", label: "Shellfish / Seafood" },
  ];

  return (
    <div style={{ maxWidth: "780px", margin: "30px auto", padding: "0 16px" }}>
      {/* Step Indicator Header */}
      <div style={{ marginBottom: "28px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px", alignItems: "center" }}>
          <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--accent-primary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Athlete Onboarding • Step {step} of 5
          </span>
          <span className="tag tag-espresso">
            {step === 1 && "Target Event"}
            {step === 2 && "Baseline Fitness"}
            {step === 3 && "Availability"}
            {step === 4 && "Profile & Safety"}
            {step === 5 && "Nutrition Context"}
          </span>
        </div>
        <div style={{ height: "6px", background: "rgba(255,255,255,0.08)", borderRadius: "var(--radius-full)", overflow: "hidden" }}>
          <div
            style={{
              height: "100%",
              width: `${(step / 5) * 100}%`,
              background: "linear-gradient(90deg, var(--accent-primary) 0%, #ff9d66 100%)",
              transition: "width 0.3s ease",
            }}
          />
        </div>
      </div>

      {error && <div className="alert-banner alert-danger">{error}</div>}

      <div className="card">
        {/* STEP 1: Target Event Setup */}
        {step === 1 && (
          <div>
            <div className="card-header">
              <div>
                <h2 className="card-title">1. Define Your Target Goal / Event</h2>
                <p className="card-subtitle">Every plan is backwards-calibrated to your specific race or fitness goal.</p>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Event or Goal Title</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Vedanta Delhi Half Marathon, First 10K Finish"
                value={eventTitle}
                onChange={(e) => setEventTitle(e.target.value)}
                required
              />
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Sport Category</label>
                <select className="form-select" value={sportType} onChange={(e) => setSportType(e.target.value)}>
                  <option value="running">Running (Road / Trail / Track)</option>
                  <option value="custom">Custom Endurance / General Fitness</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Target Distance (km)</label>
                <select
                  className="form-select"
                  value={targetDistanceKm}
                  onChange={(e) => setTargetDistanceKm(Number(e.target.value))}
                >
                  <option value={5}>5K (5.0 km)</option>
                  <option value={10}>10K (10.0 km)</option>
                  <option value={21.1}>Half Marathon (21.1 km)</option>
                  <option value={42.2}>Full Marathon (42.2 km)</option>
                  <option value={15}>15K (15.0 km)</option>
                </select>
              </div>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Target Event Date</label>
                <input
                  type="date"
                  className="form-input"
                  value={targetDate}
                  min={new Date(Date.now() + 86400000).toISOString().slice(0, 10)}
                  onChange={(e) => setTargetDate(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Target Time / Goal Description (Optional)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Sub-55 min, or Just Finish Strong"
                  value={targetTimeGoal}
                  onChange={(e) => setTargetTimeGoal(e.target.value)}
                />
              </div>
            </div>
          </div>
        )}

        {/* STEP 2: Baseline Fitness Assessment */}
        {step === 2 && (
          <div>
            <div className="card-header">
              <div>
                <h2 className="card-title">2. Baseline Fitness Assessment</h2>
                <p className="card-subtitle">
                  We use your honest starting point to calibrate safe progressive overload and deloads.
                </p>
              </div>
            </div>

            <div
              style={{
                padding: "16px",
                background: "var(--accent-primary-dim)",
                border: "1px solid rgba(255, 109, 41, 0.3)",
                borderRadius: "var(--radius-md)",
                marginBottom: "20px",
              }}
            >
              <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={hasNoBaseline}
                  onChange={(e) => setHasNoBaseline(e.target.checked)}
                  style={{ width: "18px", height: "18px", accentColor: "var(--accent-primary)" }}
                />
                <span style={{ fontWeight: 600, fontSize: "14px", color: "var(--text-primary)" }}>
                  I don't have recent training data / I am a first-time runner
                </span>
              </label>
              <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px", paddingLeft: "28px" }}>
                Selecting this uses a safe conservative walk-run ramp without fabricating paces.
              </p>
            </div>

            {!hasNoBaseline && (
              <>
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Current Weekly Volume (km / week)</label>
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      max="160"
                      className="form-input"
                      value={weeklyVolumeKm}
                      onChange={(e) => setWeeklyVolumeKm(e.target.value)}
                      required={!hasNoBaseline}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Comfortable Easy Pace (min / km)</label>
                    <input
                      type="number"
                      step="0.1"
                      min="3.0"
                      max="15.0"
                      className="form-input"
                      value={easyPaceMinKm}
                      onChange={(e) => setEasyPaceMinKm(e.target.value)}
                      placeholder="e.g. 6.3"
                    />
                  </div>
                </div>

                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Recent Time Trial / Race Distance (km)</label>
                    <input
                      type="number"
                      step="0.1"
                      min="1"
                      className="form-input"
                      value={recentRaceDistKm}
                      onChange={(e) => setRecentRaceDistKm(e.target.value)}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Recent Time (Total Minutes)</label>
                    <input
                      type="number"
                      step="0.5"
                      min="1"
                      className="form-input"
                      value={recentRaceTimeMin}
                      onChange={(e) => setRecentRaceTimeMin(e.target.value)}
                      placeholder="e.g. 54"
                    />
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* STEP 3: Availability & Time Caps */}
        {step === 3 && (
          <div>
            <div className="card-header">
              <div>
                <h2 className="card-title">3. Weekly Availability & Schedule Caps</h2>
                <p className="card-subtitle">Select which days you can train. We will never plan runs on off days.</p>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Available Training Days (Select 2 to 6 days)</label>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginTop: "8px" }}>
                {daysList.map((d) => {
                  const isSelected = availableDays.includes(d.key);
                  return (
                    <button
                      key={d.key}
                      type="button"
                      onClick={() => toggleDay(d.key)}
                      style={{
                        padding: "10px 18px",
                        borderRadius: "var(--radius-full)",
                        border: isSelected ? "1px solid var(--accent-primary)" : "1px solid var(--border-subtle)",
                        background: isSelected ? "var(--accent-primary-dim)" : "rgba(0,0,0,0.3)",
                        color: isSelected ? "var(--accent-primary)" : "var(--text-secondary)",
                        fontWeight: 600,
                        cursor: "pointer",
                        transition: "all 0.15s ease",
                      }}
                    >
                      {d.label} {isSelected ? "✓" : ""}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="grid-3" style={{ marginTop: "20px" }}>
              <div className="form-group">
                <label className="form-label">Designated Long Run Day</label>
                <select className="form-select" value={longRunDay} onChange={(e) => setLongRunDay(e.target.value)}>
                  {availableDays.map((d) => (
                    <option key={d} value={d}>
                      {d.charAt(0).toUpperCase() + d.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Max Weekday Time (min)</label>
                <input
                  type="number"
                  min="20"
                  max="180"
                  step="5"
                  className="form-input"
                  value={maxWeekdayMin}
                  onChange={(e) => setMaxWeekdayMin(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Max Weekend Time (min)</label>
                <input
                  type="number"
                  min="30"
                  max="300"
                  step="10"
                  className="form-input"
                  value={maxWeekendMin}
                  onChange={(e) => setMaxWeekendMin(e.target.value)}
                />
              </div>
            </div>
          </div>
        )}

        {/* STEP 4: Athlete Profile & Physical Readiness */}
        {step === 4 && (
          <div>
            <div className="card-header">
              <div>
                <h2 className="card-title">4. Athlete Profile & Safety Screening</h2>
                <p className="card-subtitle">Demographics are optional. Physical safety checks protect you.</p>
              </div>
            </div>

            <div className="grid-3">
              <div className="form-group">
                <label className="form-label">Display Name</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Vikram"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Age Band (Optional)</label>
                <select className="form-select" value={ageBand} onChange={(e) => setAgeBand(e.target.value)}>
                  <option value="">Prefer not to say</option>
                  <option value="18-29">18-29</option>
                  <option value="30-39">30-39</option>
                  <option value="40-49">40-49</option>
                  <option value="50-59">50-59</option>
                  <option value="60+">60+</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Region / City (Optional)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Delhi NCR, Pune"
                  value={region}
                  onChange={(e) => setRegion(e.target.value)}
                />
              </div>
            </div>

            <div style={{ marginTop: "16px", padding: "16px", background: "rgba(0,0,0,0.3)", borderRadius: "var(--radius-md)" }}>
              <strong style={{ fontSize: "14px", color: "var(--accent-amber)" }}>
                Physical Activity Readiness Screening:
              </strong>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "12px" }}>
                <label style={{ display: "flex", alignItems: "center", gap: "10px", fontSize: "13px", cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={hasChestPain}
                    onChange={(e) => setHasChestPain(e.target.checked)}
                    style={{ accentColor: "var(--accent-crimson)" }}
                  />
                  <span>Do you experience chest pain or pressure during physical exertion?</span>
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: "10px", fontSize: "13px", cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={hasDizziness}
                    onChange={(e) => setHasDizziness(e.target.checked)}
                    style={{ accentColor: "var(--accent-crimson)" }}
                  />
                  <span>Do you lose balance because of dizziness or loss of consciousness?</span>
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: "10px", fontSize: "13px", cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={hasJointPain}
                    onChange={(e) => setHasJointPain(e.target.checked)}
                    style={{ accentColor: "var(--accent-crimson)" }}
                  />
                  <span>Do you have an unmanaged bone or joint problem that could worsen?</span>
                </label>
              </div>
            </div>
          </div>
        )}

        {/* STEP 5: Nutrition & Allergies */}
        {step === 5 && (
          <div>
            <div className="card-header">
              <div>
                <h2 className="card-title">5. Indian Nutrition & Allergy Preferences</h2>
                <p className="card-subtitle">Personalized fueling guidance tailored to your culinary traditions.</p>
              </div>
            </div>

            <DisclaimerBanner type="nutrition" />

            <div className="grid-2" style={{ marginTop: "16px" }}>
              <div className="form-group">
                <label className="form-label">Dietary Preference</label>
                <select className="form-select" value={dietType} onChange={(e) => setDietType(e.target.value)}>
                  <option value="vegetarian">Vegetarian (Lacto-Veg)</option>
                  <option value="eggetarian">Eggetarian</option>
                  <option value="non_vegetarian">Non-Vegetarian</option>
                  <option value="vegan">Vegan</option>
                  <option value="jain">Jain Vegetarian (No Root Veg)</option>
                  <option value="swaminarayan">Swaminarayan (No Onion/Garlic)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Regional Indian Cuisine</label>
                <select className="form-select" value={dietRegion} onChange={(e) => setDietRegion(e.target.value)}>
                  <option value="north_indian">North Indian (Dal, Roti, Paneer, Poha)</option>
                  <option value="south_indian">South Indian (Idli, Dosa, Sambar, Upma, Curd Rice)</option>
                  <option value="west_indian">West Indian (Khichdi, Dhokla, Thepla, Usal)</option>
                  <option value="east_indian">East Indian (Sattu, Chana, Rice, Fish/Dal)</option>
                  <option value="central_indian">Central Indian (Poha-Jalebi, Dal Bafla, Sprouts)</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Food Allergies / Dietary Exclusions</label>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "10px", marginTop: "8px" }}>
                {commonAllergies.map((a) => {
                  const isChecked = allergies.includes(a.key);
                  return (
                    <label
                      key={a.key}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                        padding: "8px 12px",
                        borderRadius: "var(--radius-sm)",
                        background: isChecked ? "var(--accent-crimson-dim)" : "rgba(0,0,0,0.2)",
                        border: isChecked ? "1px solid rgba(239,68,68,0.4)" : "1px solid var(--border-subtle)",
                        cursor: "pointer",
                        fontSize: "13px",
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => toggleAllergy(a.key)}
                        style={{ accentColor: "var(--accent-crimson)" }}
                      />
                      <span style={{ color: isChecked ? "#fca5a5" : "var(--text-secondary)" }}>{a.label}</span>
                    </label>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Wizard Navigation Buttons */}
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: "28px", paddingTop: "20px", borderTop: "1px solid var(--border-subtle)" }}>
          {step > 1 ? (
            <button type="button" className="btn btn-secondary" onClick={() => setStep(step - 1)} disabled={loading}>
              ← Back
            </button>
          ) : (
            <div />
          )}

          {step < 5 ? (
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => {
                setError("");
                setStep(step + 1);
              }}
            >
              Next Step →
            </button>
          ) : (
            <button type="button" className="btn btn-primary" onClick={handleComplete} disabled={loading}>
              {loading ? "Generating Deterministic Plan..." : "⚡ Generate My SlickFit Plan →"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
