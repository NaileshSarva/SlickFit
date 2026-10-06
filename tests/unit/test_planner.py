"""Unit tests verifying deterministic planning invariants, feasibility caps, and custom event guidance."""

import datetime as dt
import pytest

from src.slickfit.domain.baseline import assess_running_baseline
from src.slickfit.domain.planner import (
    generate_initial_custom_event_plan,
    generate_initial_running_plan,
)


def test_planner_deterministic_repeatability():
    baseline = assess_running_baseline(
        experience_level="beginner",
        recent_weekly_km=15.0,
        recent_runs_per_week=3,
    )
    plan1 = generate_initial_running_plan(
        start_date_str="2026-06-01",
        event_date_str="2026-08-15",
        event_title="Bangalore 10K",
        target_distance_km=10.0,
        goal_type="finish",
        availability_days=["tuesday", "thursday", "saturday"],
        daily_time_cap_min=45,
        baseline=baseline,
    )
    plan2 = generate_initial_running_plan(
        start_date_str="2026-06-01",
        event_date_str="2026-08-15",
        event_title="Bangalore 10K",
        target_distance_km=10.0,
        goal_type="finish",
        availability_days=["tuesday", "thursday", "saturday"],
        daily_time_cap_min=45,
        baseline=baseline,
    )

    assert plan1.input_snapshot_hash == plan2.input_snapshot_hash
    assert len(plan1.seven_day_sessions) == len(plan2.seven_day_sessions)
    for s1, s2 in zip(plan1.seven_day_sessions, plan2.seven_day_sessions):
        assert s1.local_date == s2.local_date
        assert s1.session_type == s2.session_type
        assert s1.duration_min_max == s2.duration_min_max
        assert s1.distance_km_max == s2.distance_km_max


def test_planner_respects_availability_days_and_time_caps():
    baseline = assess_running_baseline(recent_weekly_km=20.0)
    avail_days = ["wednesday", "sunday"]
    time_cap = 40

    plan = generate_initial_running_plan(
        start_date_str="2026-06-01",
        event_date_str="2026-09-01",
        event_title="Hyderabad 10K",
        target_distance_km=10.0,
        goal_type="finish",
        availability_days=avail_days,
        daily_time_cap_min=time_cap,
        baseline=baseline,
    )

    for session in plan.seven_day_sessions:
        assert session.duration_min_max <= time_cap
        if session.weekday not in avail_days:
            assert session.session_type == "rest"
            assert session.priority == "rest"
            assert session.duration_min_max == 0
        else:
            assert session.session_type in ("easy_run", "long_run")


def test_planner_invariants_non_negative_finite():
    baseline = assess_running_baseline()
    plan = generate_initial_running_plan(
        start_date_str="2026-06-01",
        event_date_str="2026-07-15",
        event_title="Chennai 5K",
        target_distance_km=5.0,
        goal_type="finish",
        availability_days=["monday", "wednesday", "friday", "saturday"],
        daily_time_cap_min=60,
        baseline=baseline,
    )

    for session in plan.seven_day_sessions:
        assert session.duration_min_min >= 0
        assert session.duration_min_max >= session.duration_min_min
        if session.distance_km_min is not None:
            assert session.distance_km_min >= 0
        if session.distance_km_max is not None:
            assert session.distance_km_max >= (session.distance_km_min or 0)


def test_planner_rejects_past_or_same_day_event():
    baseline = assess_running_baseline()
    with pytest.raises(ValueError, match="Event date must be in the future"):
        generate_initial_running_plan(
            start_date_str="2026-06-10",
            event_date_str="2026-06-01",
            event_title="Past Event",
            target_distance_km=10.0,
            goal_type="finish",
            availability_days=["monday", "wednesday"],
            daily_time_cap_min=60,
            baseline=baseline,
        )


def test_custom_event_planner_generates_general_guidance():
    plan = generate_initial_custom_event_plan(
        start_date_str="2026-06-01",
        event_date_str="2026-08-01",
        event_title="State Badminton Championship",
        sport_category="badminton",
        demands_description="Multi-match tournament, agility and quick recovery",
        availability_days=["tuesday", "thursday", "saturday"],
        daily_time_cap_min=50,
    )

    assert plan.algorithm_version == "slickfit_custom_v1"
    assert "general preparation" in plan.explanation.lower()
    assert len(plan.seven_day_sessions) == 7
    active_sessions = [s for s in plan.seven_day_sessions if s.session_type != "rest"]
    assert len(active_sessions) == 3
    for sess in active_sessions:
        assert sess.session_type == "custom_practice"
        assert sess.duration_min_max <= 50
