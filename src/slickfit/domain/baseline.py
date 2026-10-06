"""Baseline evaluation, confidence scoring, and unknown-data handling.

Never fabricates baseline paces, VO2max, or maximal performance without evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BaselineAssessment:
    confidence: str  # "high" | "medium" | "low" | "unknown"
    experience_level: str  # "beginner" | "intermediate" | "advanced"
    baseline_weekly_km: float
    estimated_easy_pace_sec_per_km: Optional[int]
    has_recent_race: bool
    reasons: list[str]


def assess_running_baseline(
    experience_level: Optional[str] = None,
    recent_weekly_km: Optional[float] = None,
    recent_runs_per_week: Optional[int] = None,
    recent_race_distance_km: Optional[float] = None,
    recent_race_time_sec: Optional[int] = None,
    easy_pace_sec_per_km: Optional[int] = None,
) -> BaselineAssessment:
    """Analyze provided baseline markers and derive confidence and starting parameters.

    If inputs are missing or marked unknown, safely degrades to conservative defaults
    with low confidence and explicit reason codes.
    """
    reasons: list[str] = []
    has_recent_race = bool(
        recent_race_distance_km and recent_race_distance_km > 0 and
        recent_race_time_sec and recent_race_time_sec > 0
    )

    # 1. Experience level resolution
    exp = (experience_level or "").strip().lower()
    if exp not in ("beginner", "intermediate", "advanced"):
        exp = "beginner"
        reasons.append("EXPERIENCE_LEVEL_DEFAULTED_TO_BEGINNER")

    # 2. Starting weekly volume resolution
    if recent_weekly_km is not None and recent_weekly_km > 0:
        # Clamp to realistic bounds
        starting_weekly_km = max(5.0, min(120.0, float(recent_weekly_km)))
    else:
        # Safe conservative baseline-building base (~3 runs of 2.5-3.0 km or walk-jog intervals)
        # Without objective volume evidence, never assume high weekly mileage even if user selects intermediate/advanced
        starting_weekly_km = 9.0
        if exp in ("intermediate", "advanced"):
            reasons.append("UNVERIFIED_EXPERIENCE_CAPPED_AT_INTRODUCTORY_VOLUME")
        else:
            reasons.append("WEEKLY_VOLUME_DEFAULTED_TO_CONSERVATIVE_BASE")

    # 3. Easy pace calculation only if evidence exists
    derived_easy_pace: Optional[int] = None
    if easy_pace_sec_per_km and 180 <= easy_pace_sec_per_km <= 720:
        # User provided explicit easy pace (between 3:00/km and 12:00/km)
        derived_easy_pace = int(easy_pace_sec_per_km)
    elif has_recent_race:
        # Calculate conservative easy pace ~ 1.25x to 1.35x race pace
        race_pace_sec_km = float(recent_race_time_sec) / float(recent_race_distance_km)
        derived_easy_pace = int(race_pace_sec_km * 1.30)
        reasons.append("EASY_PACE_ESTIMATED_FROM_RECENT_RACE")
    else:
        derived_easy_pace = None
        reasons.append("EASY_PACE_UNAVAILABLE_USE_RPE_CONVERSATIONAL")

    # 4. Confidence derivation
    if has_recent_race and recent_weekly_km and recent_runs_per_week:
        confidence = "high"
    elif recent_weekly_km and (recent_runs_per_week or easy_pace_sec_per_km):
        confidence = "medium"
    elif recent_weekly_km or exp != "beginner":
        confidence = "low"
    else:
        confidence = "unknown"
        reasons.append("INSUFFICIENT_BASELINE_EVIDENCE")

    return BaselineAssessment(
        confidence=confidence,
        experience_level=exp,
        baseline_weekly_km=starting_weekly_km,
        estimated_easy_pace_sec_per_km=derived_easy_pace,
        has_recent_race=has_recent_race,
        reasons=reasons,
    )
