const API_BASE_URL = "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const isJson = response.headers.get("content-type")?.includes("application/json");
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    const message = payload?.detail || `Request failed with status ${response.status}`;
    throw new Error(Array.isArray(message) ? message.map((item) => item.msg).join(", ") : message);
  }

  return payload;
}

export function health() {
  return request("/health");
}

export function createSession(session) {
  return request("/sessions", {
    method: "POST",
    body: JSON.stringify(session),
  });
}

export function listSessions() {
  return request("/sessions");
}

export function createPerformanceTest(test) {
  return request("/performance-tests", {
    method: "POST",
    body: JSON.stringify(test),
  });
}

export function listPerformanceTests() {
  return request("/performance-tests");
}

export function fitParameters() {
  return request("/fit", { method: "POST" });
}

export function latestParams() {
  return request("/params/latest");
}

export function runTaper(payload) {
  return request("/taper", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
