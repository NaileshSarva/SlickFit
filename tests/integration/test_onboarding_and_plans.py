"""Integration tests for onboarding flow, baseline intake, and plan retrieval."""

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
        db_path = Path(tmpdir) / "test_onboarding.db"
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


def _get_auth_token(client: TestClient, email: str = "athlete@slickfit.local") -> str:
    res = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "TestPassword123!", "full_name": "Test Athlete"},
    )
    return res.json()["access_token"]


def test_complete_onboarding_for_running_event_with_unknown_baseline(client_with_db):
    client = client_with_db
    token = _get_auth_token(client, "runner.intro@slickfit.local")
    auth_header = {"Authorization": f"Bearer {token}"}

    # Verify onboarding status is initially incomplete
    status_res = client.get("/api/v1/onboarding/status", headers=auth_header)
    assert status_res.status_code == 200
    assert status_res.json()["onboarding_completed"] is False

    # Perform onboarding with future event and completely unknown baseline
    future_date = (dt.date.today() + dt.timedelta(days=60)).isoformat()
    onboard_payload = {
        "event": {
            "kind": "running",
            "sport": "running",
            "title": "Airtel Delhi Half Marathon 10K",
            "event_date": future_date,
            "goal_type": "finish",
            "target_value": 10.0,
            "target_unit": "km",
        },
        "baseline": {
            "experience_level": None,
            "recent_weekly_km": None,
            "recent_runs_per_week": None,
        },
        "availability": {
            "training_days": ["tuesday", "thursday", "saturday"],
            "daily_time_cap_min": 50,
        },
        "profile": {
            "age_band": "25-29",
            "region": "North India",
        },
        "nutrition": {
            "dietary_pattern": "vegetarian",
            "allergies": ["peanuts"],
        },
    }

    onboard_res = client.post("/api/v1/onboarding", headers=auth_header, json=onboard_payload)
    assert onboard_res.status_code == 201
    data = onboard_res.json()
    assert data["event"]["title"] == "Airtel Delhi Half Marathon 10K"
    assert data["event"]["status"] == "active"
    assert data["plan"]["algorithm_version"] == "slickfit_v1_rules"
    assert len(data["plan"]["sessions"]) == 7

    # Check status now reflects completed onboarding
    status_after = client.get("/api/v1/onboarding/status", headers=auth_header)
    assert status_after.json()["onboarding_completed"] is True

    # Check /api/v1/plans/current
    current_plan_res = client.get("/api/v1/plans/current", headers=auth_header)
    assert current_plan_res.status_code == 200
    plan_data = current_plan_res.json()
    assert plan_data["event_title"] == "Airtel Delhi Half Marathon 10K"
    assert plan_data["days_until_event"] == 60
    assert len(plan_data["sessions"]) == 7

    # Verify session limits
    for sess in plan_data["sessions"]:
        assert sess["duration_min_max"] <= 50


def test_complete_onboarding_for_custom_event(client_with_db):
    client = client_with_db
    token = _get_auth_token(client, "trekker@slickfit.local")
    auth_header = {"Authorization": f"Bearer {token}"}

    future_date = (dt.date.today() + dt.timedelta(days=45)).isoformat()
    custom_payload = {
        "event": {
            "kind": "custom",
            "sport": "trekking",
            "title": "Himalayan High Altitude Trek",
            "event_date": future_date,
            "goal_type": "finish",
            "demands": {"description": "Endurance trekking with 10kg backpack"},
        },
        "availability": {
            "training_days": ["monday", "wednesday", "friday", "sunday"],
            "daily_time_cap_min": 60,
        },
    }

    onboard_res = client.post("/api/v1/onboarding", headers=auth_header, json=custom_payload)
    assert onboard_res.status_code == 201
    data = onboard_res.json()
    assert data["event"]["kind"] == "custom"
    assert data["plan"]["algorithm_version"] == "slickfit_custom_v1"


def test_tenant_isolation_on_plans_and_events(client_with_db):
    client = client_with_db
    token_a = _get_auth_token(client, "user_a@slickfit.local")
    token_b = _get_auth_token(client, "user_b@slickfit.local")

    future_date = (dt.date.today() + dt.timedelta(days=30)).isoformat()
    client.post(
        "/api/v1/onboarding",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "event": {"kind": "running", "title": "User A Event", "event_date": future_date},
            "availability": {"training_days": ["tuesday", "thursday"]},
        },
    )

    # User B should have NO active plan yet
    res_b_plan = client.get("/api/v1/plans/current", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b_plan.status_code == 404
    assert "No active training plan found" in res_b_plan.json()["message"]
