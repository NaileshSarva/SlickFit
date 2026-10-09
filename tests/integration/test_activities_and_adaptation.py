"""Integration tests for workout logging, recovery check-ins, adaptations, and history."""

import datetime as dt
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.slickfit.api.app import app
from src.slickfit.db.base import Base
from src.slickfit.db.session import get_db


@pytest.fixture
def client_with_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_act.db"
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

        def override_get_db():
            db = TestingSession()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        try:
            with TestClient(app) as client:
                yield client
        finally:
            app.dependency_overrides.clear()


def _setup_athlete_with_plan(client: TestClient) -> dict[str, str]:
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "runner.active@slickfit.local", "password": "ActivePassword2026!"},
    )
    token = reg.json()["access_token"]
    auth_header = {"Authorization": f"Bearer {token}"}

    future_date = (dt.date.today() + dt.timedelta(days=45)).isoformat()
    onboard = client.post(
        "/api/v1/onboarding",
        headers=auth_header,
        json={
            "event": {"kind": "running", "title": "Pune 10K", "event_date": future_date, "target_value": 10.0},
            "availability": {"training_days": ["tuesday", "thursday", "saturday"], "daily_time_cap_min": 60},
        },
    )
    plan_data = onboard.json()["plan"]
    first_session_id = plan_data["sessions"][0]["id"]
    return {"token": token, "session_id": first_session_id}


def test_activity_logging_and_correction_flow(client_with_db):
    client = client_with_db
    setup = _setup_athlete_with_plan(client)
    auth_header = {"Authorization": f"Bearer {setup['token']}"}
    today = dt.date.today().isoformat()

    # Log workout
    log_res = client.post(
        "/api/v1/activities",
        headers=auth_header,
        json={
            "planned_session_id": setup["session_id"],
            "local_date": today,
            "activity_type": "running",
            "duration_min": 42.5,
            "distance_km": 5.4,
            "perceived_effort": 6,
            "completion_state": "completed",
            "notes": "Felt smooth and steady",
        },
    )
    assert log_res.status_code == 201
    act_id = log_res.json()["id"]

    # Correct activity distance with amendment reason
    patch_res = client.patch(
        f"/api/v1/activities/{act_id}",
        headers=auth_header,
        json={
            "distance_km": 5.8,
            "change_reason": "GPS calibration correction from manual track check",
        },
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["distance_km"] == 5.8

    # Verify amendment record is accessible in /api/v1/data/amendments
    amend_res = client.get("/api/v1/data/amendments", headers=auth_header)
    assert amend_res.status_code == 200
    assert len(amend_res.json()) >= 1
    assert amend_res.json()[0]["prior_value"] == "5.4"
    assert amend_res.json()[0]["replacement_value"] == "5.8"


def test_unknown_planned_session_is_rejected(client_with_db):
    client = client_with_db
    setup = _setup_athlete_with_plan(client)
    response = client.post(
        "/api/v1/activities",
        headers={"Authorization": f"Bearer {setup['token']}"},
        json={
            "planned_session_id": "not-a-real-session",
            "local_date": dt.date.today().isoformat(),
            "activity_type": "running",
            "duration_min": 20,
        },
    )
    assert response.status_code == 404
    assert response.json()["message"] == "Planned session not found."


def test_planned_session_cannot_be_logged_twice(client_with_db):
    client = client_with_db
    setup = _setup_athlete_with_plan(client)
    auth_header = {"Authorization": f"Bearer {setup['token']}"}
    payload = {
        "planned_session_id": setup["session_id"],
        "local_date": dt.date.today().isoformat(),
        "activity_type": "running",
        "duration_min": 20,
        "completion_state": "completed",
    }
    assert client.post("/api/v1/activities", headers=auth_header, json=payload).status_code == 201
    duplicate = client.post("/api/v1/activities", headers=auth_header, json=payload)
    assert duplicate.status_code == 409


def test_recovery_checkin_triggers_adaptation(client_with_db):
    client = client_with_db
    setup = _setup_athlete_with_plan(client)
    auth_header = {"Authorization": f"Bearer {setup['token']}"}
    today = dt.date.today().isoformat()

    # Record low recovery check-in
    checkin_res = client.post(
        "/api/v1/checkins",
        headers=auth_header,
        json={
            "local_date": today,
            "sleep_duration_hours": 4.5,
            "sleep_quality": 2,
            "energy_level": 1,
            "soreness_level": 4,
            "stress_level": 4,
            "pain_flag": False,
        },
    )
    assert checkin_res.status_code == 201

    # Verify history returns new plan revision
    history_res = client.get("/api/v1/plans/history", headers=auth_header)
    assert history_res.status_code == 200
    revisions = history_res.json()
    assert len(revisions) >= 2
    assert "LOW_RECOVERY" in revisions[0]["explanation"] or "recovery" in revisions[0]["explanation"].lower()

    # Reprocessing the same stale recovery signal must not keep creating revisions.
    from sqlalchemy import select
    from src.slickfit.db.models import Plan, PlanRevision
    db = client_with_db.app.dependency_overrides[get_db]()
    db = next(db)
    from src.slickfit.domain.adaptation import AdaptationService
    from src.slickfit.auth.security import decode_access_token
    user_id = decode_access_token(setup["token"])["sub"]
    current_revision = AdaptationService.process_adaptation(db, user_id, trigger_reason="DAILY_CHECKIN")
    revisions_after_repeat = db.execute(
        select(PlanRevision).join(Plan).where(Plan.user_id == user_id)
    ).scalars().all()
    assert len(revisions_after_repeat) == len(revisions)
    db.close()


def test_unified_history_and_progress_endpoints(client_with_db):
    client = client_with_db
    setup = _setup_athlete_with_plan(client)
    auth_header = {"Authorization": f"Bearer {setup['token']}"}
    today = dt.date.today().isoformat()

    # Log an activity first
    client.post(
        "/api/v1/activities",
        headers=auth_header,
        json={
            "local_date": today,
            "activity_type": "running",
            "duration_min": 30.0,
            "distance_km": 4.0,
            "perceived_effort": 5,
            "completion_state": "completed",
        },
    )

    history_res = client.get("/api/v1/history", headers=auth_header)
    assert history_res.status_code == 200
    items = history_res.json()
    assert len(items) >= 1

    progress_res = client.get("/api/v1/progress", headers=auth_header)
    assert progress_res.status_code == 200
    pdata = progress_res.json()
    assert "total_runs_completed" in pdata
    assert "consistency_rate_pct" in pdata
