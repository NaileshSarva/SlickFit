import tempfile
from contextlib import contextmanager
from pathlib import Path

from fastapi.testclient import TestClient

from src.peakforge.api import app, get_store
from src.peakforge.storage import PeakForgeStore


@contextmanager
def api_client():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "api-test.db"

        def override_store():
            store = PeakForgeStore(db_path)
            try:
                yield store
            finally:
                store.close()

        app.dependency_overrides[get_store] = override_store
        try:
            yield TestClient(app)
        finally:
            app.dependency_overrides.clear()


def seed_history(client: TestClient) -> None:
    sessions = [
        ("2026-01-01", 50, 5, ""),
        ("2026-01-02", 45, 6, ""),
        ("2026-01-03", 60, 5, ""),
        ("2026-01-04", 30, 4, ""),
        ("2026-01-05", 70, 6, ""),
        ("2026-01-06", 40, 5, ""),
    ]
    for date, duration_min, intensity, notes in sessions:
        response = client.post(
            "/sessions",
            json={
                "date": date,
                "duration_min": duration_min,
                "intensity": intensity,
                "notes": notes,
            },
        )
        assert response.status_code == 200

    tests = [
        ("2026-01-01", 100.0),
        ("2026-01-03", 107.0),
        ("2026-01-06", 103.0),
    ]
    for date, score in tests:
        response = client.post("/performance-tests", json={"date": date, "score": score})
        assert response.status_code == 200


def test_add_and_list_sessions():
    with api_client() as client:
        created = client.post(
            "/sessions",
            json={
                "date": "2026-02-01",
                "duration_min": 75,
                "intensity": 6.5,
                "notes": "Tempo",
            },
        )

        assert created.status_code == 200
        assert created.json() == {
            "date": "2026-02-01",
            "load": 487.5,
            "notes": "Tempo",
        }

        listed = client.get("/sessions")
        assert listed.status_code == 200
        assert listed.json() == [created.json()]


def test_add_and_list_performance_tests():
    with api_client() as client:
        created = client.post(
            "/performance-tests",
            json={"date": "2026-02-03", "score": 321.5},
        )

        assert created.status_code == 200
        assert created.json() == {"date": "2026-02-03", "score": 321.5}

        listed = client.get("/performance-tests")
        assert listed.status_code == 200
        assert listed.json() == [created.json()]


def test_fit_endpoint_end_to_end():
    with api_client() as client:
        seed_history(client)

        response = client.post("/fit")

        assert response.status_code == 200
        data = response.json()
        assert set(data["params"]) == {"k1", "k2", "tau1", "tau2", "p0", "residual_error"}
        assert data["simulation"]["dates"] == [
            "2026-01-01",
            "2026-01-02",
            "2026-01-03",
            "2026-01-04",
            "2026-01-05",
            "2026-01-06",
        ]
        assert len(data["simulation"]["fitness"]) == 6
        assert len(data["simulation"]["fatigue"]) == 6
        assert len(data["simulation"]["performance"]) == 6

        latest = client.get("/params/latest")
        assert latest.status_code == 200
        assert latest.json() == data["params"]


def test_taper_endpoint_end_to_end_after_fitting():
    with api_client() as client:
        seed_history(client)
        fit_response = client.post("/fit")
        assert fit_response.status_code == 200

        response = client.post(
            "/taper",
            json={
                "days_until_event": 5,
                "constraints": {"max_daily_load": 90, "min_daily_load": 0},
                "config": {
                    "population_size": 12,
                    "generations": 8,
                    "elite_count": 2,
                    "tournament_size": 3,
                    "seed": 42,
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["best_loads"]) == 5
        assert len(data["fitness_history"]) == 8
        assert isinstance(data["predicted_peak_performance"], float)
        assert len(data["simulation"]["dates"]) == 11
        assert data["simulation"]["dates"][-1] == "2026-01-11"
        assert len(data["simulation"]["performance"]) == 11
