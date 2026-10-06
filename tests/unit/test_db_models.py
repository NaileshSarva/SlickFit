"""Unit tests verifying SQLAlchemy database models, relationships, and constraints."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.slickfit.db.base import Base
from src.slickfit.db.models import (
    Activity,
    ActivityRevision,
    AdaptationEvent,
    AthleteProfile,
    Availability,
    BaselineObservation,
    DailyCheckIn,
    DataAmendment,
    Event,
    NutritionGuidance,
    NutritionProfile,
    Plan,
    PlannedSession,
    PlanRevision,
    User,
)


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, expire_on_commit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


def test_user_creation_and_cascade_relationships(test_db):
    user = User(
        email="test.athlete@slickfit.local",
        hashed_password="hashed_pass_placeholder",
        full_name="Vikram Seth",
        timezone="Asia/Kolkata",
    )
    test_db.add(user)
    test_db.commit()

    assert user.id is not None
    assert user.timezone == "Asia/Kolkata"
    assert user.locale == "en-IN"
    assert user.units == "metric"

    # Profile & Availability
    profile = AthleteProfile(user_id=user.id, age_band="30-39", height_cm=175.0, weight_kg=70.0)
    availability = Availability(user_id=user.id, daily_time_cap_min=75)
    event = Event(user_id=user.id, kind="running", sport="running", title="Tata Mumbai Marathon 10K", event_date="2026-01-18")

    test_db.add_all([profile, availability, event])
    test_db.commit()

    # Plan with PlanRevision and PlannedSession
    plan = Plan(user_id=user.id, event_id=event.id, algorithm_version="slickfit_v1_rules")
    test_db.add(plan)
    test_db.commit()

    rev = PlanRevision(
        plan_id=plan.id,
        user_id=user.id,
        revision_number=1,
        input_snapshot_hash="hash123",
        start_date="2026-01-01",
        end_date="2026-01-07",
        explanation="Initial 7-day introductory plan",
    )
    test_db.add(rev)
    test_db.commit()

    session = PlannedSession(
        plan_revision_id=rev.id,
        user_id=user.id,
        local_date="2026-01-01",
        session_type="easy_run",
        purpose="Aerobic base building",
        duration_min_min=30,
        duration_min_max=40,
        priority="medium",
    )
    test_db.add(session)
    test_db.commit()

    # Actual activity and revision
    activity = Activity(
        user_id=user.id,
        planned_session_id=session.id,
        local_date="2026-01-01",
        activity_type="running",
        duration_min=35.0,
        distance_km=5.2,
        perceived_effort=5,
        completion_state="completed",
    )
    test_db.add(activity)
    test_db.commit()

    act_rev = ActivityRevision(
        activity_id=activity.id,
        user_id=user.id,
        revision_number=1,
        duration_min=35.0,
        distance_km=5.2,
        perceived_effort=5,
        completion_state="completed",
        change_reason="Initial save",
    )
    test_db.add(act_rev)
    test_db.commit()

    # Daily checkin
    checkin = DailyCheckIn(
        user_id=user.id,
        local_date="2026-01-01",
        sleep_duration_hours=7.5,
        sleep_quality=4,
        energy_level=4,
        soreness_level=1,
        stress_level=2,
    )
    test_db.add(checkin)
    test_db.commit()

    # Verify query
    fetched_user = test_db.get(User, user.id)
    assert fetched_user is not None
    assert fetched_user.profile.height_cm == 175.0
    assert len(fetched_user.events) == 1
    assert len(fetched_user.plans) == 1
    assert len(fetched_user.activities) == 1
    assert len(fetched_user.checkins) == 1

    # Cascade delete verification
    test_db.delete(fetched_user)
    test_db.commit()

    assert test_db.get(AthleteProfile, profile.id) is None
    assert test_db.get(Event, event.id) is None
    assert test_db.get(Plan, plan.id) is None
    assert test_db.get(Activity, activity.id) is None
