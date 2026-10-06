/**
 * SlickFit API Client
 * Connects to versioned /api/v1 backend endpoints with JWT/cookie authentication.
 */

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

let authToken = localStorage.getItem("slickfit_token") || "";

export function setAuthToken(token) {
  authToken = token || "";
  if (token) {
    localStorage.setItem("slickfit_token", token);
  } else {
    localStorage.removeItem("slickfit_token");
  }
}

export function getAuthToken() {
  return authToken;
}

async function apiRequest(endpoint, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    let errorDetail = "An unexpected error occurred.";
    try {
      const errJson = await response.json();
      errorDetail = errJson.message || errJson.detail || JSON.stringify(errJson);
    } catch {
      errorDetail = `HTTP ${response.status} ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

// -- Auth Endpoints --
export async function registerUser(payload) {
  const res = await apiRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (res.access_token) setAuthToken(res.access_token);
  return res;
}

export async function loginUser(payload) {
  const res = await apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (res.access_token) setAuthToken(res.access_token);
  return res;
}

export async function demoLogin(demoKey = "demo1") {
  const res = await apiRequest("/auth/demo-login", {
    method: "POST",
    body: JSON.stringify({ demo_key: demoKey }),
  });
  if (res.access_token) setAuthToken(res.access_token);
  return res;
}

export async function getMe() {
  return apiRequest("/me");
}

export async function updateMe(payload) {
  return apiRequest("/me", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function logoutUser() {
  try {
    await apiRequest("/auth/logout", { method: "POST" });
  } finally {
    setAuthToken("");
  }
}

// -- Onboarding Endpoints --
export async function getOnboardingStatus() {
  return apiRequest("/onboarding/status");
}

export async function submitOnboarding(payload) {
  return apiRequest("/onboarding", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// -- Events Endpoints --
export async function listEvents() {
  return apiRequest("/events");
}

export async function getActiveEvent() {
  return apiRequest("/events/active");
}

export async function createEvent(payload) {
  return apiRequest("/events", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// -- Plans Endpoints --
export async function getCurrentPlan() {
  return apiRequest("/plans/current");
}

export async function getPlanHistory() {
  return apiRequest("/plans/history");
}

// -- Activities Endpoints --
export async function logActivity(payload) {
  return apiRequest("/activities", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listActivities() {
  return apiRequest("/activities");
}

export async function correctActivity(activityId, payload) {
  return apiRequest(`/activities/${activityId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

// -- Check-Ins Endpoints --
export async function recordCheckIn(payload) {
  return apiRequest("/checkins", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getTodayCheckIn() {
  try {
    return await apiRequest("/checkins/today");
  } catch {
    return null;
  }
}

// -- Nutrition Endpoints --
export async function getTodayNutrition() {
  return apiRequest("/nutrition/today");
}

// -- History & Progress Endpoints --
export async function getUnifiedHistory() {
  return apiRequest("/history");
}

export async function getProgressTrends() {
  return apiRequest("/progress");
}

export async function listAmendments() {
  return apiRequest("/data/amendments");
}
