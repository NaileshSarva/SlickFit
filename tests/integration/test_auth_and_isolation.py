"""Integration tests proving authentication, demo account switcher, and tenant isolation."""

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
def client_with_isolated_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_auth.db"
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


def test_health_and_readiness_no_private_data(client_with_isolated_db):
    res_health = client_with_isolated_db.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"
    assert "email" not in res_health.json()

    res_ready = client_with_isolated_db.get("/ready")
    assert res_ready.status_code == 200
    assert res_ready.json() == {"status": "ready"}


def test_registration_and_login_flow(client_with_isolated_db):
    client = client_with_isolated_db

    # Register
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "aarav.patel@slickfit.local",
            "password": "SecurePassword123!",
            "full_name": "Aarav Patel",
            "timezone": "Asia/Kolkata",
        },
    )
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert data["email"] == "aarav.patel@slickfit.local"
    assert "access_token" in data
    token = data["access_token"]

    # Access /api/v1/auth/me with bearer token
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "aarav.patel@slickfit.local"
    assert me_data["full_name"] == "Aarav Patel"
    assert me_data["profile"]["age_band"] == ""
    assert me_data["profile"]["region"] == ""

    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "aarav.patel@slickfit.local",
            "password": "SecurePassword123!",
        },
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


def test_real_account_registration_has_no_fabricated_demographics(client_with_isolated_db):
    """Regression test: prove a new real account has zero fabricated age_band or region."""
    client = client_with_isolated_db
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "unbiased.runner@slickfit.local",
            "password": "CleanPassword2026!",
            "full_name": "Kavita Rao",
        },
    )
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]

    me_res = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    profile = me_res.json()["profile"]
    assert profile["age_band"] == "", "Age band must not be fabricated"
    assert profile["region"] == "", "Region must not be fabricated"
    assert profile["height_cm"] is None
    assert profile["weight_kg"] is None


def test_invalid_login_and_validation_errors(client_with_isolated_db):
    client = client_with_isolated_db

    # Wrong password
    bad_login = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@slickfit.local", "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401
    err_json = bad_login.json()
    assert err_json["code"] == "HTTP_401"
    assert "Invalid email or password" in err_json["message"]
    assert "request_id" in err_json

    # Short password validation error
    short_pw_res = client.post(
        "/api/v1/auth/register",
        json={"email": "test@slickfit.local", "password": "short"},
    )
    assert short_pw_res.status_code == 422
    val_err = short_pw_res.json()
    assert val_err["code"] == "VALIDATION_ERROR"
    assert len(val_err["field_errors"]) > 0


def test_activity_list_rejects_unbounded_and_nonpositive_limits(client_with_isolated_db):
    client = client_with_isolated_db
    registration = client.post(
        "/api/v1/auth/register",
        json={"email": "limits@slickfit.local", "password": "ValidPassword123!"},
    )
    headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}
    assert client.get("/api/v1/activities?limit=100000", headers=headers).status_code == 422
    assert client.get("/api/v1/activities?limit=0", headers=headers).status_code == 422


def test_profile_settings_update_persists_athlete_and_nutrition_preferences(client_with_isolated_db):
    client = client_with_isolated_db
    registration = client.post(
        "/api/v1/auth/register",
        json={"email": "profile.edit@slickfit.local", "password": "ValidPassword123!"},
    )
    headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}
    response = client.patch(
        "/api/v1/me",
        headers=headers,
        json={
            "full_name": "Asha Athlete", "age_band": "30-39", "sex": "female",
            "height_cm": 168, "weight_kg": 61.5, "region": "Pune",
            "timezone": "Asia/Kolkata", "units": "metric",
            "dietary_pattern": "vegan", "regional_preference": "west_indian",
            "allergies": ["none", "peanuts", "peanuts"], "foods_avoided": ["mushrooms"],
            "intake_target_kcal": 2200,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["profile"]["weight_kg"] == 61.5
    assert data["nutrition_profile"]["dietary_pattern"] == "vegan"
    assert data["nutrition_profile"]["allergies_json"] == '["peanuts"]'


def test_demo_login_accounts_and_tenant_isolation(client_with_isolated_db):
    client = client_with_isolated_db

    # Log into Demo User 1 (10K runner)
    demo1_res = client.post("/api/v1/auth/demo-login", json={"demo_key": "demo1"})
    assert demo1_res.status_code == 200
    demo1_token = demo1_res.json()["access_token"]
    demo1_user_id = demo1_res.json()["user_id"]

    # Log into Demo User 2 (Baseline builder)
    demo2_res = client.post("/api/v1/auth/demo-login", json={"demo_key": "demo2"})
    assert demo2_res.status_code == 200
    demo2_token = demo2_res.json()["access_token"]
    demo2_user_id = demo2_res.json()["user_id"]

    assert demo1_user_id != demo2_user_id

    # Verify User 1 receives User 1's profile
    me1 = client.get("/api/v1/me", headers={"Authorization": f"Bearer {demo1_token}"})
    assert me1.status_code == 200
    assert me1.json()["id"] == demo1_user_id
    assert "Arjun" in me1.json()["full_name"]

    # Verify User 2 receives User 2's profile
    me2 = client.get("/api/v1/me", headers={"Authorization": f"Bearer {demo2_token}"})
    assert me2.status_code == 200
    assert me2.json()["id"] == demo2_user_id
    assert "Priya" in me2.json()["full_name"]

    # Update User 1 full name
    patch_res = client.patch(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {demo1_token}"},
        json={"full_name": "Arjun Sharma Updated"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["full_name"] == "Arjun Sharma Updated"

    # User 2 profile must remain unchanged
    me2_after = client.get("/api/v1/me", headers={"Authorization": f"Bearer {demo2_token}"})
    assert "Priya" in me2_after.json()["full_name"]
    assert me2_after.json()["full_name"] != "Arjun Sharma Updated"


def test_unauthorized_access_rejections(client_with_isolated_db):
    client = client_with_isolated_db

    # No token
    res_no_token = client.get("/api/v1/me")
    assert res_no_token.status_code == 401

    # Malformed token
    res_bad_token = client.get("/api/v1/me", headers={"Authorization": "Bearer gibberish.token.value"})
    assert res_bad_token.status_code == 401


def test_demo_login_disabled_when_demo_mode_false(client_with_isolated_db, monkeypatch):
    from src.slickfit.config import settings

    monkeypatch.setattr(settings, "raw_demo_mode", "false")
    assert settings.demo_mode_enabled is False

    res = client_with_isolated_db.post("/api/v1/auth/demo-login", json={"demo_key": "demo1"})
    assert res.status_code == 403
    assert "disabled" in res.json()["message"].lower()
