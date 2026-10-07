import React, { useState } from "react";
import { submitOnboarding } from "../api.js";
import DisclaimerBanner from "../components/DisclaimerBanner.jsx";

const SPORTS_LIST = [
  { id: "running", name: "Running", defaultTitle: "Vedanta Delhi Half Marathon" },
  { id: "cycling", name: "Cycling", defaultTitle: "Tour of Nilgiris / Gran Fondo" },
  { id: "swimming", name: "Swimming", defaultTitle: "Open Water Sea Swim" },
  { id: "triathlon", name: "Triathlon", defaultTitle: "Goa Olympic Distance Triathlon" },
  { id: "football", name: "Football", defaultTitle: "State League Championship" },
  { id: "cricket", name: "Cricket", defaultTitle: "Corporate Weekend League" },
  { id: "badminton", name: "Badminton", defaultTitle: "District Ranking Tournament" },
  { id: "basketball", name: "Basketball", defaultTitle: "Inter-City 5v5 Tournament" },
  { id: "tennis", name: "Tennis", defaultTitle: "Club Championship" },
  { id: "volleyball", name: "Volleyball", defaultTitle: "State Invitational" },
  { id: "kabaddi", name: "Kabaddi", defaultTitle: "District Pro Kabaddi Cup" },
  { id: "athletics", name: "Athletics (Track & Field)", defaultTitle: "State Masters Athletic Meet" },
  { id: "strength", name: "Strength Training", defaultTitle: "Hypertrophy & Strength Cycle" },
  { id: "weightlifting", name: "Weightlifting (Olympic)", defaultTitle: "State Weightlifting Championship" },
  { id: "powerlifting", name: "Powerlifting", defaultTitle: "National Powerlifting Meet" },
  { id: "hiking", name: "Hiking / Trekking", defaultTitle: "Rohtang Pass / Valley Trek" },
  { id: "fitness", name: "General Fitness", defaultTitle: "12-Week Conditioning Foundation" },
  { id: "other", name: "Other Sport", defaultTitle: "Personal Performance Milestone" },
  { id: "custom", name: "Custom Event", defaultTitle: "Custom Endurance Challenge" },
];

export default function Onboarding({ onOnboardingComplete }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Step 1: Sport & Event Definition
  const [sport, setSport] = useState("running");
  const [eventTitle, setEventTitle] = useState("Vedanta Delhi Half Marathon");
  const [targetDate, setTargetDate] = useState(
    new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
  );
  const [goalType, setGoalType] = useState("finish");
  const [goalDescription, setGoalDescription] = useState("");

  // Sport-specific event details
  // Running
  const [runningDistanceKm, setRunningDistanceKm] = useState("21.1");
  const [runningTerrain, setRunningTerrain] = useState("road");
  // Cycling
  const [cyclingType, setCyclingType] = useState("gran_fondo");
  const [cyclingDistanceKm, setCyclingDistanceKm] = useState("100");
  const [cyclingElevationM, setCyclingElevationM] = useState("");
  // Swimming
  const [swimmingDistanceM, setSwimmingDistanceM] = useState("1500");
  const [swimmingEnvironment, setSwimmingEnvironment] = useState("open_water");
  const [swimmingStroke, setSwimmingStroke] = useState("freestyle");
  // Team / Racket Sports (Football, Cricket, Badminton, etc.)
  const [sportFormat, setSportFormat] = useState("11v11");
  const [sportRole, setSportRole] = useState("Midfielder");
  const [matchFrequency, setMatchFrequency] = useState("1-2 matches per week");
  // Strength / Powerlifting
  const [strengthLifts, setStrengthLifts] = useState("Squat, Bench, Deadlift");
  const [targetWeightClass, setTargetWeightClass] = useState("");

  // Step 2: Baseline Assessment
  const [hasNoBaseline, setHasNoBaseline] = useState(false);
  const [experienceLevel, setExperienceLevel] = useState("intermediate");
  const [weeklyVolume, setWeeklyVolume] = useState("20");
  const [recentRaceDist, setRecentRaceDist] = useState("10");
  const [recentRaceTimeMin, setRecentRaceTimeMin] = useState("54");
  const [easyPaceMinKm, setEasyPaceMinKm] = useState("6.2");
  const [strengthCurrent1RM, setStrengthCurrent1RM] = useState("");

  // Step 3: Availability & Time Caps
  const [availableDays, setAvailableDays] = useState(["tuesday", "thursday", "saturday", "sunday"]);
  const [dailyTimeCapMin, setDailyTimeCapMin] = useState(60);
  const [preferredTimes, setPreferredTimes] = useState(["morning"]);

  // Step 4: Profile & Safety Screening
  const [ageBand, setAgeBand] = useState("");
  const [sex, setSex] = useState("");
  const [heightCm, setHeightCm] = useState("");
  const [weightKg, setWeightKg] = useState("");
  const [region, setRegion] = useState("");
  const [hasChestPain, setHasChestPain] = useState(false);
  const [hasDizziness, setHasDizziness] = useState(false);
  const [hasJointPain, setHasJointPain] = useState(false);

  // Step 5: Nutrition & Allergies
  const [dietType, setDietType] = useState("vegetarian");
  const [dietRegion, setDietRegion] = useState("south_indian");
  const [allergies, setAllergies] = useState([]);
  const [foodsAvoided, setFoodsAvoided] = useState([]);
  const [calorieTarget, setCalorieTarget] = useState("");
  const [activityLevel, setActivityLevel] = useState("moderate");

  function handleSportChange(newSport) {
    setSport(newSport);
    const found = SPORTS_LIST.find((s) => s.id === newSport);
    if (found) {
      setEventTitle(found.defaultTitle);
    }
  }

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

  function toggleAllergy(allergyKey) {
    if (allergies.includes(allergyKey)) {
      setAllergies(allergies.filter((a) => a !== allergyKey));
    } else {
      setAllergies([...allergies, allergyKey]);
    }
  }

  async function handleComplete(e) {
    if (e) e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // Build dynamic sport demands payload
      const demands = {
        sport_category: sport,
      };

      let targetValue = null;
      let targetUnit = "km";

      if (sport === "running") {
        targetValue = Number(runningDistanceKm) || 10.0;
        targetUnit = "km";
        demands.terrain = runningTerrain;
        demands.goal_description = goalDescription;
      } else if (sport === "cycling") {
        targetValue = Number(cyclingDistanceKm) || 50.0;
        targetUnit = "km";
        demands.event_type = cyclingType;
        demands.elevation_m = Number(cyclingElevationM) || null;
        demands.description = `${cyclingType.replace(/_/g, " ")} (${targetValue} km)`;
      } else if (sport === "swimming") {
        targetValue = Number(swimmingDistanceM) || 1500;
        targetUnit = "meters";
        demands.environment = swimmingEnvironment;
        demands.stroke = swimmingStroke;
        demands.description = `${swimmingDistanceM}m ${swimmingStroke} (${swimmingEnvironment})`;
      } else if (["strength", "weightlifting", "powerlifting"].includes(sport)) {
        targetValue = null;
        targetUnit = "kg";
        demands.lifts = strengthLifts;
        demands.weight_class = targetWeightClass;
        demands.description = `${sport} focus: ${strengthLifts}`;
      } else if (["football", "cricket", "badminton", "basketball", "tennis", "volleyball", "kabaddi"].includes(sport)) {
        targetValue = null;
        targetUnit = "matches";
        demands.format = sportFormat;
        demands.role = sportRole;
        demands.match_frequency = matchFrequency;
        demands.description = `${sport} (${sportFormat}, ${sportRole})`;
      } else {
        targetValue = null;
        targetUnit = "goal";
        demands.description = goalDescription || `${sport} preparation`;
      }

      const payload = {
        event: {
          kind: sport === "running" ? "running" : sport,
          sport: sport,
          title: eventTitle.trim() || `${sport.toUpperCase()} Event`,
          event_date: targetDate,
          goal_type: goalType,
          target_value: targetValue,
          target_unit: targetUnit,
          demands: demands,
          notes: goalDescription.trim() || "",
        },
        baseline: {
          experience_level: experienceLevel,
          recent_weekly_km: hasNoBaseline || sport !== "running" ? null : (Number(weeklyVolume) || null),
          recent_runs_per_week: hasNoBaseline ? null : availableDays.length,
          recent_race_distance_km: hasNoBaseline || sport !== "running" ? null : (Number(recentRaceDist) || null),
          recent_race_time_sec:
            hasNoBaseline || !recentRaceTimeMin ? null : Math.round(Number(recentRaceTimeMin) * 60),
          easy_pace_sec_per_km:
            hasNoBaseline || !easyPaceMinKm ? null : Math.round(Number(easyPaceMinKm) * 60),
        },
        availability: {
          training_days: availableDays,
          daily_time_cap_min: Number(dailyTimeCapMin) || 60,
          preferred_times: preferredTimes,
          environment_equipment: sport === "running" ? "road_outdoor" : "standard_facilities",
        },
        profile: {
          age_band: ageBand.trim() || null,
          sex: sex.trim() || null,
          height_cm: heightCm ? Number(heightCm) : null,
          weight_kg: weightKg ? Number(weightKg) : null,
          region: region.trim() || null,
        },
        nutrition: {
          dietary_pattern: dietType,
          regional_preference: dietRegion,
          allergies: allergies,
          foods_avoided: foodsAvoided,
          goal_preference: "endurance_fueling",
          intake_target_kcal: calorieTarget ? Number(calorieTarget) : null,
          activity_level: activityLevel,
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
    <div style={{ maxWidth: "800px", margin: "30px auto", padding: "0 16px" }}>
      {/* Wizard Step Indicator */}
      <div style={{ marginBottom: "28px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px", alignItems: "center" }}>
          <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--accent-primary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Athlete Onboarding • Step {step} of 5
          </span>
          <span className="tag tag-espresso">
            {step === 1 && "Sport & Target Event"}
            {step === 2 && "Baseline Fitness"}
            {step === 3 && "Availability & Schedule"}
            {step === 4 && "Athlete Profile & Safety"}
            {step === 5 && "Nutrition & Preferences"}
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
        {/* STEP 1: Sport Selection & Dynamic Event Configuration */}
        {step === 1 && (
          <div>
            <div className="card-header">
              <div>
                <h2 className="card-title">1. Sport Category & Target Event</h2>
                <p className="card-subtitle">
                  SlickFit calibrates your schedule specifically for your selected sport and target milestone.
                </p>
              </div>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Sport Category</label>
                <select
                  className="form-select"
                  value={sport}
                  onChange={(e) => handleSportChange(e.target.value)}
                >
                  {SPORTS_LIST.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Event or Milestone Title</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. State Championship, 10K Finish"
                  value={eventTitle}
                  onChange={(e) => setEventTitle(e.target.value)}
                  required
                />
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
                <label className="form-label">Goal Strategy</label>
                <select
                  className="form-select"
                  value={goalType}
                  onChange={(e) => setGoalType(e.target.value)}
                >
                  <option value="finish">Complete & Finish Strong</option>
                  <option value="target_time">Target Time / Performance Goal</option>
                  <option value="build_capacity">Build Work Capacity & Stamina</option>
                  <option value="general_fitness">General Fitness & Skill Practice</option>
                </select>
              </div>
            </div>

            {/* DYNAMIC SPORT-SPECIFIC QUESTIONNAIRE FIELDS */}
            {sport === "running" && (
              <div style={{ marginTop: "16px", padding: "16px", background: "rgba(0,0,0,0.25)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
                <h4 style={{ fontSize: "13px", fontWeight: 700, color: "var(--accent-primary)", marginBottom: "12px", textTransform: "uppercase" }}>
                  Running Event Specifics
                </h4>
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Target Distance (km)</label>
                    <select
                      className="form-select"
                      value={runningDistanceKm}
                      onChange={(e) => setRunningDistanceKm(e.target.value)}
                    >
                      <option value="5">5K (5.0 km)</option>
                      <option value="10">10K (10.0 km)</option>
                      <option value="21.1">Half Marathon (21.1 km)</option>
                      <option value="42.2">Full Marathon (42.2 km)</option>
                      <option value="15">15K (15.0 km)</option>
                      <option value="50">Ultra (50.0 km)</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Course Terrain</label>
                    <select
                      className="form-select"
                      value={runningTerrain}
                      onChange={(e) => setRunningTerrain(e.target.value)}
                    >
                      <option value="road">Road / Pavement</option>
                      <option value="trail">Trail / Off-Road</option>
                      <option value="track">Synthetic Track</option>
                      <option value="treadmill">Treadmill</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {sport === "cycling" && (
              <div style={{ marginTop: "16px", padding: "16px", background: "rgba(0,0,0,0.25)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
                <h4 style={{ fontSize: "13px", fontWeight: 700, color: "var(--accent-primary)", marginBottom: "12px", textTransform: "uppercase" }}>
                  Cycling Event Specifics
                </h4>
                <div className="grid-3">
                  <div className="form-group">
                    <label className="form-label">Ride Format</label>
                    <select className="form-select" value={cyclingType} onChange={(e) => setCyclingType(e.target.value)}>
                      <option value="gran_fondo">Gran Fondo / Century</option>
                      <option value="road_race">Road Race</option>
                      <option value="time_trial">Individual Time Trial</option>
                      <option value="criterium">Criterium / Circuit</option>
                      <option value="endurance_tour">Endurance Touring / Brevet</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Target Distance (km)</label>
                    <input
                      type="number"
                      min="10"
                      max="1000"
                      className="form-input"
                      value={cyclingDistanceKm}
                      onChange={(e) => setCyclingDistanceKm(e.target.value)}
                      placeholder="e.g. 100"
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Expected Elevation Gain (m, Optional)</label>
                    <input
                      type="number"
                      min="0"
                      max="10000"
                      className="form-input"
                      value={cyclingElevationM}
                      onChange={(e) => setCyclingElevationM(e.target.value)}
                      placeholder="e.g. 1200"
                    />
                  </div>
                </div>
              </div>
            )}

            {sport === "swimming" && (
              <div style={{ marginTop: "16px", padding: "16px", background: "rgba(0,0,0,0.25)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
                <h4 style={{ fontSize: "13px", fontWeight: 700, color: "var(--accent-primary)", marginBottom: "12px", textTransform: "uppercase" }}>
                  Swimming Event Specifics
                </h4>
                <div className="grid-3">
                  <div className="form-group">
                    <label className="form-label">Environment</label>
                    <select className="form-select" value={swimmingEnvironment} onChange={(e) => setSwimmingEnvironment(e.target.value)}>
                      <option value="open_water">Open Water (Sea / Lake)</option>
                      <option value="50m_pool">50m Olympic Pool</option>
                      <option value="25m_pool">25m Short Course Pool</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Target Distance (meters)</label>
                    <input
                      type="number"
                      min="50"
                      max="25000"
                      step="50"
                      className="form-input"
                      value={swimmingDistanceM}
                      onChange={(e) => setSwimmingDistanceM(e.target.value)}
                      placeholder="e.g. 1500"
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Primary Stroke</label>
                    <select className="form-select" value={swimmingStroke} onChange={(e) => setSwimmingStroke(e.target.value)}>
                      <option value="freestyle">Freestyle / Front Crawl</option>
                      <option value="breaststroke">Breaststroke</option>
                      <option value="backstroke">Backstroke</option>
                      <option value="butterfly">Butterfly</option>
                      <option value="medley">Individual Medley</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {["football", "cricket", "badminton", "basketball", "tennis", "volleyball", "kabaddi"].includes(sport) && (
              <div style={{ marginTop: "16px", padding: "16px", background: "rgba(0,0,0,0.25)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
                <h4 style={{ fontSize: "13px", fontWeight: 700, color: "var(--accent-primary)", marginBottom: "12px", textTransform: "uppercase" }}>
                  Match & Role Specifics ({sport.charAt(0).toUpperCase() + sport.slice(1)})
                </h4>
                <div className="grid-3">
                  <div className="form-group">
                    <label className="form-label">Format</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g. 11v11, T20, Singles, 5v5"
                      value={sportFormat}
                      onChange={(e) => setSportFormat(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Playing Position / Role</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g. Midfielder, Fast Bowler, Raider"
                      value={sportRole}
                      onChange={(e) => setSportRole(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Match Frequency</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g. 1 match per weekend"
                      value={matchFrequency}
                      onChange={(e) => setMatchFrequency(e.target.value)}
                    />
                  </div>
                </div>
              </div>
            )}

            {["strength", "weightlifting", "powerlifting"].includes(sport) && (
              <div style={{ marginTop: "16px", padding: "16px", background: "rgba(0,0,0,0.25)", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
                <h4 style={{ fontSize: "13px", fontWeight: 700, color: "var(--accent-primary)", marginBottom: "12px", textTransform: "uppercase" }}>
                  Strength & Lifting Specifics
                </h4>
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Primary Lifts / Focus</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g. Squat, Bench Press, Deadlift"
                      value={strengthLifts}
                      onChange={(e) => setStrengthLifts(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Weight Class / Equipment (Optional)</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g. Under 83kg / Raw"
                      value={targetWeightClass}
                      onChange={(e) => setTargetWeightClass(e.target.value)}
                    />
                  </div>
                </div>
              </div>
            )}

            <div className="form-group" style={{ marginTop: "14px" }}>
              <label className="form-label">Target Goal Description / Notes (Optional)</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Sub-1h50min, Peak competition readiness, Injury prevention"
                value={goalDescription}
                onChange={(e) => setGoalDescription(e.target.value)}
              />
            </div>
          </div>
        )}

        {/* STEP 2: Baseline Fitness Assessment */}
        {step === 2 && (
          <div>
            <div className="card-header">
              <div>
                <h2 className="card-title">2. Baseline Fitness & Training History</h2>
                <p className="card-subtitle">
                  Provide your honest starting point to calibrate safe progressive overload and deloads.
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
                  I am starting fresh / No recent baseline history
                </span>
              </label>
              <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px", paddingLeft: "28px" }}>
                Select this to start with a safe conservative foundation without fabricating metrics.
              </p>
            </div>

            {!hasNoBaseline && (
              <>
                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">Athlete Experience Level</label>
                    <select
                      className="form-select"
                      value={experienceLevel}
                      onChange={(e) => setExperienceLevel(e.target.value)}
                    >
                      <option value="beginner">Beginner (0-1 year consistent training)</option>
                      <option value="intermediate">Intermediate (1-3 years)</option>
                      <option value="advanced">Advanced (3+ years)</option>
                    </select>
                  </div>

                  {sport === "running" ? (
                    <div className="form-group">
                      <label className="form-label">Current Weekly Volume (km / week)</label>
                      <input
                        type="number"
                        step="0.5"
                        min="0"
                        max="250"
                        className="form-input"
                        value={weeklyVolume}
                        onChange={(e) => setWeeklyVolume(e.target.value)}
                      />
                    </div>
                  ) : (
                    <div className="form-group">
                      <label className="form-label">Recent Training Sessions / Week</label>
                      <input
                        type="number"
                        min="1"
                        max="14"
                        className="form-input"
                        value={weeklyVolume}
                        onChange={(e) => setWeeklyVolume(e.target.value)}
                      />
                    </div>
                  )}
                </div>

                {sport === "running" && (
                  <div className="grid-3">
                    <div className="form-group">
                      <label className="form-label">Comfortable Easy Pace (min/km)</label>
                      <input
                        type="number"
                        step="0.1"
                        min="3.0"
                        max="18.0"
                        className="form-input"
                        value={easyPaceMinKm}
                        onChange={(e) => setEasyPaceMinKm(e.target.value)}
                        placeholder="e.g. 6.2"
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Recent Benchmark Dist (km)</label>
                      <input
                        type="number"
                        step="0.1"
                        min="1"
                        max="100"
                        className="form-input"
                        value={recentRaceDist}
                        onChange={(e) => setRecentRaceDist(e.target.value)}
                        placeholder="e.g. 10"
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Recent Time (Minutes)</label>
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
                )}
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
                <p className="card-subtitle">Select which days you can train. We will never plan workouts on off days.</p>
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

            <div className="grid-2" style={{ marginTop: "20px" }}>
              <div className="form-group">
                <label className="form-label">Daily Available Training Time Cap (min)</label>
                <input
                  type="number"
                  min="20"
                  max="240"
                  step="5"
                  className="form-input"
                  value={dailyTimeCapMin}
                  onChange={(e) => setDailyTimeCapMin(Number(e.target.value))}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Preferred Training Time</label>
                <select
                  className="form-select"
                  value={preferredTimes[0] || "morning"}
                  onChange={(e) => setPreferredTimes([e.target.value])}
                >
                  <option value="early_morning">Early Morning (5 AM - 7 AM)</option>
                  <option value="morning">Morning (7 AM - 9 AM)</option>
                  <option value="evening">Evening (5 PM - 8 PM)</option>
                  <option value="night">Night (8 PM+)</option>
                </select>
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
                <p className="card-subtitle">Demographics are optional. Physical safety screening protects your health.</p>
              </div>
            </div>

            <div className="grid-3">
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
                <label className="form-label">Weight (kg, Optional)</label>
                <input
                  type="number"
                  step="0.5"
                  min="30"
                  max="250"
                  className="form-input"
                  placeholder="e.g. 68"
                  value={weightKg}
                  onChange={(e) => setWeightKg(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Region / City (Optional)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Delhi NCR, Bengaluru"
                  value={region}
                  onChange={(e) => setRegion(e.target.value)}
                />
              </div>
            </div>

            <div style={{ marginTop: "16px", padding: "16px", background: "rgba(0,0,0,0.3)", borderRadius: "var(--radius-md)" }}>
              <strong style={{ fontSize: "14px", color: "var(--accent-amber)" }}>
                Physical Activity Readiness Check:
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
                  <span>Do you have an unmanaged bone or joint problem that could worsen with exercise?</span>
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
                <h2 className="card-title">5. Indian Nutrition & Dietary Preferences</h2>
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
                  <option value="jain">Jain Vegetarian (No Root Veg / Satvik)</option>
                  <option value="swaminarayan">Swaminarayan (Satvik / No Onion-Garlic)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Regional Indian Cuisine</label>
                <select className="form-select" value={dietRegion} onChange={(e) => setDietRegion(e.target.value)}>
                  <option value="south_indian">South Indian (Idli, Dosa, Sambar, Ragi, Curd)</option>
                  <option value="north_indian">North Indian (Dal, Roti, Paneer, Chana, Rajma)</option>
                  <option value="west_indian">West Indian (Khichdi, Dhokla, Thepla, Usal)</option>
                  <option value="east_indian">East Indian (Sattu, Dalma, Fish/Rice, Chana)</option>
                  <option value="central_indian">Central Indian (Poha, Dal Bafla, Sprouts)</option>
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
              Back
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
              Next Step
            </button>
          ) : (
            <button type="button" className="btn btn-primary" onClick={handleComplete} disabled={loading}>
              {loading ? "Generating Plan..." : "Generate My SlickFit Plan"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
