"""Local SQLite persistence layer — training sessions, performance tests,
and fitted athlete parameters. No external database server required.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import AthleteParams, PerformanceTest, TrainingSession

DEFAULT_DB_PATH = Path.home() / ".peakforge" / "peakforge.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    load REAL NOT NULL,
    notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS performance_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    score REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS athlete_params (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    k1 REAL NOT NULL,
    k2 REAL NOT NULL,
    tau1 REAL NOT NULL,
    tau2 REAL NOT NULL,
    p0 REAL NOT NULL,
    residual_error REAL NOT NULL,
    fitted_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


class PeakForgeStore:
    """Thin wrapper around a local SQLite database file."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # -- sessions ---------------------------------------------------
    def add_session(self, session: TrainingSession) -> int:
        cur = self._conn.execute(
            "INSERT INTO sessions (date, load, notes) VALUES (?, ?, ?)",
            (session.date, session.load, session.notes),
        )
        self._conn.commit()
        return cur.lastrowid

    def list_sessions(self) -> list[TrainingSession]:
        rows = self._conn.execute(
            "SELECT date, load, notes FROM sessions ORDER BY date ASC"
        ).fetchall()
        return [TrainingSession(date=r[0], load=r[1], notes=r[2]) for r in rows]

    # -- performance tests -------------------------------------------
    def add_performance_test(self, test: PerformanceTest) -> int:
        cur = self._conn.execute(
            "INSERT INTO performance_tests (date, score) VALUES (?, ?)",
            (test.date, test.score),
        )
        self._conn.commit()
        return cur.lastrowid

    def list_performance_tests(self) -> list[PerformanceTest]:
        rows = self._conn.execute(
            "SELECT date, score FROM performance_tests ORDER BY date ASC"
        ).fetchall()
        return [PerformanceTest(date=r[0], score=r[1]) for r in rows]

    # -- athlete params ------------------------------------------------
    def save_params(self, params: AthleteParams) -> int:
        cur = self._conn.execute(
            "INSERT INTO athlete_params (k1, k2, tau1, tau2, p0, residual_error) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (params.k1, params.k2, params.tau1, params.tau2, params.p0, params.residual_error),
        )
        self._conn.commit()
        return cur.lastrowid

    def latest_params(self) -> AthleteParams | None:
        row = self._conn.execute(
            "SELECT k1, k2, tau1, tau2, p0, residual_error FROM athlete_params "
            "ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        return AthleteParams(k1=row[0], k2=row[1], tau1=row[2], tau2=row[3], p0=row[4], residual_error=row[5])
