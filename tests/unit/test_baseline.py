"""Unit tests for baseline assessment and unknown-data handling."""

import pytest

from src.slickfit.domain.baseline import assess_running_baseline


def test_baseline_assessment_with_full_race_evidence():
    assessment = assess_running_baseline(
        experience_level="intermediate",
        recent_weekly_km=35.0,
        recent_runs_per_week=4,
        recent_race_distance_km=10.0,
        recent_race_time_sec=3000,  # 50 min 10K = 5:00/km
    )
    assert assessment.confidence == "high"
    assert assessment.experience_level == "intermediate"
    assert assessment.baseline_weekly_km == 35.0
    assert assessment.has_recent_race is True
    # 5:00/km (300 sec) * 1.30 = 390 sec/km (6:30/km)
    assert assessment.estimated_easy_pace_sec_per_km == 390
    assert "EASY_PACE_ESTIMATED_FROM_RECENT_RACE" in assessment.reasons


def test_baseline_assessment_with_explicit_easy_pace():
    assessment = assess_running_baseline(
        experience_level="beginner",
        recent_weekly_km=15.0,
        recent_runs_per_week=3,
        easy_pace_sec_per_km=420,  # 7:00/km
    )
    assert assessment.confidence == "medium"
    assert assessment.estimated_easy_pace_sec_per_km == 420


def test_baseline_assessment_with_unknown_data_no_fabrication():
    assessment = assess_running_baseline(
        experience_level=None,
        recent_weekly_km=None,
        recent_runs_per_week=None,
        recent_race_distance_km=None,
        recent_race_time_sec=None,
        easy_pace_sec_per_km=None,
    )
    assert assessment.confidence == "unknown"
    assert assessment.experience_level == "beginner"
    assert assessment.baseline_weekly_km == 9.0  # Conservative safe beginner base (~3x3km walk/run)
    assert assessment.estimated_easy_pace_sec_per_km is None, "Must not fabricate pace without evidence"
    assert "INSUFFICIENT_BASELINE_EVIDENCE" in assessment.reasons
    assert "EASY_PACE_UNAVAILABLE_USE_RPE_CONVERSATIONAL" in assessment.reasons


def test_baseline_weekly_volume_clamping():
    assessment_huge = assess_running_baseline(recent_weekly_km=500.0)
    assert assessment_huge.baseline_weekly_km == 120.0

    assessment_tiny = assess_running_baseline(recent_weekly_km=2.0)
    assert assessment_tiny.baseline_weekly_km == 5.0


def test_unverified_intermediate_advanced_experience_capped_at_safe_introductory_volume():
    """When a runner self-identifies as advanced or intermediate but provides no volume history,

    never assume 20 or 35 km/wk. Cap at safe introductory 9.0 km/wk baseline.
    """
    adv_assessment = assess_running_baseline(
        experience_level="advanced",
        recent_weekly_km=None,
    )
    assert adv_assessment.baseline_weekly_km == 9.0
    assert "UNVERIFIED_EXPERIENCE_CAPPED_AT_INTRODUCTORY_VOLUME" in adv_assessment.reasons

    int_assessment = assess_running_baseline(
        experience_level="intermediate",
        recent_weekly_km=None,
    )
    assert int_assessment.baseline_weekly_km == 9.0
    assert "UNVERIFIED_EXPERIENCE_CAPPED_AT_INTRODUCTORY_VOLUME" in int_assessment.reasons
