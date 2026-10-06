import { useEffect, useState } from "react";
import {
  createPerformanceTest,
  createSession,
  fitParameters,
  listPerformanceTests,
  listSessions,
  runTaper,
} from "./api.js";
import SessionForm from "./components/SessionForm.jsx";
import PerformanceTestForm from "./components/PerformanceTestForm.jsx";
import FitPanel from "./components/FitPanel.jsx";
import TaperPanel from "./components/TaperPanel.jsx";
import FormCurveChart from "./components/FormCurveChart.jsx";

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [tests, setTests] = useState([]);
  const [params, setParams] = useState(null);
  const [fitCurve, setFitCurve] = useState(null);
  const [taperResult, setTaperResult] = useState(null);
  const [message, setMessage] = useState("");

  async function refreshHistory() {
    const [nextSessions, nextTests] = await Promise.all([listSessions(), listPerformanceTests()]);
    setSessions(nextSessions);
    setTests(nextTests);
  }

  useEffect(() => {
    refreshHistory().catch((error) => setMessage(error.message));
  }, []);

  async function handleCreateSession(payload) {
    const session = await createSession(payload);
    setSessions((current) => [...current, session].sort((a, b) => a.date.localeCompare(b.date)));
    setMessage(`Session logged for ${session.date} with load ${session.load.toFixed(1)}.`);
  }

  async function handleCreateTest(payload) {
    const test = await createPerformanceTest(payload);
    setTests((current) => [...current, test].sort((a, b) => a.date.localeCompare(b.date)));
    setMessage(`Performance test logged for ${test.date}.`);
  }

  async function handleFit() {
    const result = await fitParameters();
    setParams(result.params);
    setFitCurve(result.simulation);
    setTaperResult(null);
    setMessage("Parameters fitted and form curve updated.");
  }

  async function handleTaper(daysUntilEvent) {
    const result = await runTaper({
      days_until_event: daysUntilEvent,
      config: { generations: 150 },
    });
    setTaperResult(result);
    setMessage("Optimal taper computed.");
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Physiological Performance-Simulation & Optimal Taper Engine</p>
          <h1>PeakForge</h1>
        </div>
        <div className="history-summary" aria-label="Logged history summary">
          <span>{sessions.length} sessions</span>
          <span>{tests.length} tests</span>
        </div>
      </header>

      {message && <div className="status-message">{message}</div>}

      <section className="workflow-grid">
        <SessionForm onSubmit={handleCreateSession} />
        <PerformanceTestForm onSubmit={handleCreateTest} />
        <FitPanel params={params} onFit={handleFit} />
        <TaperPanel result={taperResult} onRun={handleTaper} disabled={!params} />
      </section>

      <section className="history-grid">
        <div className="panel">
          <div className="panel-heading">
            <span className="step">History</span>
            <h2>Training Sessions</h2>
          </div>
          <div className="compact-list">
            {sessions.length === 0 ? (
              <p className="muted">No training sessions logged yet.</p>
            ) : (
              sessions.slice(-6).map((session) => (
                <div className="list-row" key={`${session.date}-${session.load}-${session.notes}`}>
                  <span>{session.date}</span>
                  <strong>{session.load.toFixed(1)}</strong>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <span className="step">Benchmarks</span>
            <h2>Performance Tests</h2>
          </div>
          <div className="compact-list">
            {tests.length === 0 ? (
              <p className="muted">No performance tests logged yet.</p>
            ) : (
              tests.slice(-6).map((test) => (
                <div className="list-row" key={`${test.date}-${test.score}`}>
                  <span>{test.date}</span>
                  <strong>{test.score.toFixed(1)}</strong>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      <FormCurveChart fitCurve={fitCurve} taperCurve={taperResult?.simulation} />
    </main>
  );
}
