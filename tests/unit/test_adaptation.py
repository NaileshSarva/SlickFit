"""Unit tests for the deterministic adaptation engine, reason codes, and safety stops."""

import pytest

from src.slickfit.db.models import Activity, DailyCheckIn, PlannedSession
from src.slickfit.domain.adaptation import evaluate_adaptation


def _mock_planned_sessions() -> list[PlannedSession]:
    s1 = PlannedSession(
        id="s1",
        user_id="u1",
        plan_revision_id="r1",
        local_date="2026-06-02",
        session_type="easy_run",
        purpose="Aerobic maintenance",
        duration_min_min=30,
        duration_min_max=40,
        distance_km_min=4.0,
        distance_km_max=5.0,
        effort_target="Easy / Conversational (RPE 3-4)",
        blocks_json="[]",
        priority="medium",
        flexibility_window_days=1,
        status="scheduled",
        reason_codes_json="[]",
    )
    s2 = PlannedSession(
        id="s2",
        user_id="u1",
        plan_revision_id="r1",
        local_date="2026-06-04",
        session_type="tempo",
        purpose="Lactate threshold tempo",
        duration_min_min=35,
        duration_min_max=45,
        distance_km_min=5.0,
        distance_km_max=6.5,
        effort_target="Moderate / Tempo (RPE 6-7)",
        blocks_json="[]",
        priority="high",
        flexibility_window_days=1,
        status="scheduled",
        reason_codes_json="[]",
    )
    return [s1, s2]


def test_red_flag_safety_stop_suppresses_exercise():
    sessions = _mock_planned_sessions()
    checkin = DailyCheckIn(
        user_id="u1",
        local_date="2026-06-02",
        red_flag_symptom=True,
        notes="Chest tightness and dizziness during stairs",
    )

    decision = evaluate_adaptation(
        current_sessions=sessions,
        latest_checkin=checkin,
        today_str="2026-06-02",
    )

    assert decision.should_adapt is True
    assert decision.safety_stop is True
    assert "RED_FLAG_SAFETY_STOP" in decision.reason_codes
    assert "URGENT SAFETY STOP" in decision.explanation
    assert len(decision.adjusted_sessions) == 0


def test_pain_report_mitigates_to_gentle_walk_or_rest():
    sessions = _mock_planned_sessions()
    checkin = DailyCheckIn(
        user_id="u1",
        local_date="2026-06-02",
        pain_flag=True,
        pain_area="Right Achilles Tendon",
        pain_severity=5,
    )

    decision = evaluate_adaptation(
        current_sessions=sessions,
        latest_checkin=checkin,
        today_str="2026-06-02",
    )

    assert decision.should_adapt is True
    assert decision.safety_stop is False
    assert "PAIN_REPORTED" in decision.reason_codes
    for s in decision.adjusted_sessions:
        assert s["session_type"] == "recovery_walk"
        assert s["duration_min_max"] <= 25
        assert "ADAPTED_FOR_PAIN_MITIGATION" in s["reason_codes"]


def test_low_recovery_reduces_volume():
    sessions = _mock_planned_sessions()
    checkin = DailyCheckIn(
        user_id="u1",
        local_date="2026-06-02",
        energy_level=1,
        soreness_level=4,
        sleep_quality=2,
    )

    decision = evaluate_adaptation(
        current_sessions=sessions,
        latest_checkin=checkin,
        today_str="2026-06-02",
    )

    assert decision.should_adapt is True
    assert "LOW_RECOVERY" in decision.reason_codes
    # s1 was 40 min max, reduced by 25% -> 30 min max
    assert decision.adjusted_sessions[0]["duration_min_max"] == 30


def test_missed_session_does_not_stack_volume():
    sessions = _mock_planned_sessions()
    skipped_act = Activity(
        user_id="u1",
        local_date="2026-06-02",
        completion_state="skipped",
        notes="Missed due to work emergency",
    )

    decision = evaluate_adaptation(
        current_sessions=sessions,
        recent_activities=[skipped_act],
        today_str="2026-06-02",
    )

    assert decision.should_adapt is True
    assert "MISSED_SESSION_SAFELY_DROPPED" in decision.reason_codes
    assert "dropped rather than stacked" in decision.explanation
