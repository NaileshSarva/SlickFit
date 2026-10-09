import React, { useState, useEffect } from "react";
import {
  getMe,
  getOnboardingStatus,
  getCurrentPlan,
  getActiveEvent,
  getTodayCheckIn,
  getTodayNutrition,
  logoutUser,
  getAuthToken,
} from "./api.js";

import Navbar from "./components/Navbar.jsx";
import Landing from "./views/Landing.jsx";
import Onboarding from "./views/Onboarding.jsx";
import Home from "./views/Home.jsx";
import Plan from "./views/Plan.jsx";
import Train from "./views/Train.jsx";
import Nutrition from "./views/Nutrition.jsx";
import Progress from "./views/Progress.jsx";
import Profile from "./views/Profile.jsx";

export default function App() {
  const [user, setUser] = useState(null);
  const [onboardingCompleted, setOnboardingCompleted] = useState(false);
  const [activeTab, setActiveTab] = useState("home");

  // App data state
  const [currentPlan, setCurrentPlan] = useState(null);
  const [activeEvent, setActiveEvent] = useState(null);
  const [todayCheckIn, setTodayCheckIn] = useState(null);
  const [todayNutrition, setTodayNutrition] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadUserSession() {
    setLoading(true);
    setError("");

    try {
      const token = getAuthToken();
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }

      const userData = await getMe();
      setUser(userData);

      const status = await getOnboardingStatus();
      setOnboardingCompleted(Boolean(status?.onboarding_completed || status?.has_completed_onboarding));

      if (status?.onboarding_completed || status?.has_completed_onboarding) {
        await refreshAppData();
      }
    } catch (err) {
      // If token expired or invalid, reset
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  async function refreshAppData() {
    try {
      const [planRes, eventRes, checkinRes, nutritionRes] = await Promise.all([
        getCurrentPlan().catch(() => null),
        getActiveEvent().catch(() => null),
        getTodayCheckIn().catch(() => null),
        getTodayNutrition().catch(() => null),
      ]);
      setCurrentPlan(planRes);
      setActiveEvent(eventRes);
      setTodayCheckIn(checkinRes);
      setTodayNutrition(nutritionRes);
    } catch (err) {
      console.error("Failed to refresh app data", err);
    }
  }

  useEffect(() => {
    loadUserSession();
  }, []);

  async function handleAuthSuccess(authResult) {
    if (authResult?.user) {
      setUser(authResult.user);
    }
    await loadUserSession();
  }

  async function handleLogout() {
    await logoutUser();
    setUser(null);
    setCurrentPlan(null);
    setActiveEvent(null);
    setTodayCheckIn(null);
    setTodayNutrition(null);
    setActiveTab("home");
  }

  function handleOnboardingComplete(result) {
    setOnboardingCompleted(true);
    if (result?.plan) setCurrentPlan(result.plan);
    if (result?.event) setActiveEvent(result.event);
    refreshAppData();
    setActiveTab("home");
  }

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center" }}>
          <div className="spinner" style={{ margin: "0 auto 16px auto" }} />
          <p style={{ color: "var(--text-secondary)", fontSize: "14px" }}>Loading SlickFit Coach...</p>
        </div>
      </div>
    );
  }

  // Not authenticated -> Show Landing with 1-Click Demo switchers & Real account sign-in
  if (!user) {
    return <Landing onAuthSuccess={handleAuthSuccess} />;
  }

  // Authenticated but onboarding incomplete -> Show 5-step Onboarding Wizard
  if (!onboardingCompleted) {
    return (
      <main className="app-container">
        <header className="top-nav" style={{ justifyContent: "space-between" }}>
          <div className="brand-section">
            <div className="brand-logo">
              SlickFit
            </div>
            {user?.is_demo && <span className="brand-badge">Demo Mode</span>}
          </div>
          <button type="button" className="btn btn-secondary btn-sm" onClick={handleLogout}>
            Sign Out
          </button>
        </header>

        <Onboarding onOnboardingComplete={handleOnboardingComplete} />
      </main>
    );
  }

  // Authenticated and onboarded -> Full SlickFit App Shell
  return (
    <main className="app-container">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user}
        activeEvent={activeEvent}
        onLogout={handleLogout}
      />

      {error && <div className="alert-banner alert-danger">{error}</div>}

      {activeTab === "home" && (
        <Home
          user={user}
          activeEvent={activeEvent}
          currentPlan={currentPlan}
          todayCheckIn={todayCheckIn}
          todayNutrition={todayNutrition}
          onNavigateTab={setActiveTab}
          onRefreshData={refreshAppData}
        />
      )}

      {activeTab === "plan" && (
        <Plan
          currentPlan={currentPlan}
          activeEvent={activeEvent}
          onNavigateTab={setActiveTab}
          onRefreshData={refreshAppData}
        />
      )}

      {activeTab === "train" && (
        <Train
          currentPlan={currentPlan}
          todayCheckIn={todayCheckIn}
          activeEvent={activeEvent}
          onWorkoutLogged={refreshAppData}
          onNavigateTab={setActiveTab}
        />
      )}

      {activeTab === "nutrition" && (
        <Nutrition
          todayNutrition={todayNutrition}
          user={user}
        />
      )}

      {activeTab === "progress" && (
        <Progress
          onRefreshData={refreshAppData}
        />
      )}

      {activeTab === "profile" && (
        <Profile
          user={user}
          activeEvent={activeEvent}
          onUserUpdated={async (updatedUser) => { setUser(updatedUser); await refreshAppData(); }}
          onLogout={handleLogout}
        />
      )}
    </main>
  );
}
