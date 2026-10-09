"""Deterministic running-first and custom-event planning engine.

Provides transparent, rule-based, feasibility-checked training prescriptions
with immutable revisioning and explainable reason codes.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from .baseline import BaselineAssessment, assess_running_baseline

PLANNER_ALGORITHM_VERSION = "slickfit_v1_rules"

WEEKDAY_NAMES = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


@dataclass
class PlannedWorkoutBlock:
    name: str  # "warmup" | "main_set" | "cooldown"
    description: str
    duration_min: int


@dataclass
class GeneratedSession:
    local_date: str
    weekday: str
    session_type: str  # "easy_run" | "long_run" | "tempo" | "intervals" | "rest" | "recovery_walk" | "custom_practice"
    purpose: str
    duration_min_min: int
    duration_min_max: int
    distance_unit: str
    distance_km_min: Optional[float]
    distance_km_max: Optional[float]
    effort_target: str
    blocks: list[PlannedWorkoutBlock]
    target_pace_sec_per_km: Optional[int]
    priority: str  # "high" | "medium" | "low" | "rest"
    flexibility_window_days: int
    reason_codes: list[str]


@dataclass
class PlanPhase:
    name: str
    start_date: str
    end_date: str
    focus: str
    weekly_mileage_target_km: float


@dataclass
class MilestoneCheck:
    target_date: str
    title: str
    description: str
    criteria: str


@dataclass
class GeneratedPlanOutput:
    algorithm_version: str
    input_snapshot_hash: str
    start_date: str
    end_date: str
    days_until_event: int
    phases: list[PlanPhase]
    milestones: list[MilestoneCheck]
    seven_day_sessions: list[GeneratedSession]
    explanation: str
    trigger_reason: str
    confidence: str
    limitations: str


def compute_snapshot_hash(data: dict[str, Any]) -> str:
    """Compute deterministic SHA-256 hash of planner inputs."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]


def generate_initial_running_plan(
    start_date_str: str,
    event_date_str: str,
    event_title: str,
    target_distance_km: float,
    goal_type: str,
    availability_days: list[str],
    daily_time_cap_min: int,
    baseline: BaselineAssessment,
    timezone: str = "Asia/Kolkata",
) -> GeneratedPlanOutput:
    """Generate a deterministic, feasibility-bounded running plan for an upcoming event."""
    # 1. Parse dates and validate horizon
    start_date = dt.date.fromisoformat(start_date_str)
    event_date = dt.date.fromisoformat(event_date_str)
    horizon_days = (event_date - start_date).days

    if horizon_days <= 0:
        raise ValueError("Event date must be in the future.")

    # 2. Normalize availability days
    avail_days_set = {d.strip().lower() for d in availability_days if d.strip().lower() in WEEKDAY_NAMES}
    if len(avail_days_set) < 2:
        # Fallback to standard 3-day schedule if fewer than 2 days provided
        avail_days_set = {"tuesday", "thursday", "saturday"}

    time_cap = max(20, min(180, int(daily_time_cap_min)))

    # 3. Snapshot hash inputs for idempotency and audit trail
    input_snapshot = {
        "start_date": start_date_str,
        "event_date": event_date_str,
        "target_distance_km": target_distance_km,
        "goal_type": goal_type,
        "availability_days": sorted(list(avail_days_set)),
        "daily_time_cap_min": time_cap,
        "baseline": asdict(baseline),
        "timezone": timezone,
        "algorithm_version": PLANNER_ALGORITHM_VERSION,
    }
    snapshot_hash = compute_snapshot_hash(input_snapshot)

    # 4. Plan phase division
    total_weeks = max(1, horizon_days // 7)
    base_weeks = max(1, int(total_weeks * 0.40))
    build_weeks = max(1, int(total_weeks * 0.35))
    peak_weeks = max(1, total_weeks - base_weeks - build_weeks - 1) if total_weeks > 3 else 0
    taper_weeks = 1 if total_weeks >= 3 else 0

    phases: list[PlanPhase] = []
    current_phase_start = start_date

    # Base Phase
    base_end = current_phase_start + dt.timedelta(days=base_weeks * 7 - 1)
    phases.append(
        PlanPhase(
            name="Base Aerobic Consistency",
            start_date=current_phase_start.isoformat(),
            end_date=min(event_date, base_end).isoformat(),
            focus="Establish routine, develop tendon resiliency, and build aerobic volume with conversational running.",
            weekly_mileage_target_km=round(baseline.baseline_weekly_km, 1),
        )
    )
    current_phase_start = base_end + dt.timedelta(days=1)

    # Build Phase
    if current_phase_start < event_date:
        build_end = current_phase_start + dt.timedelta(days=build_weeks * 7 - 1)
        phases.append(
            PlanPhase(
                name="Stamina & Distance Extension",
                start_date=current_phase_start.isoformat(),
                end_date=min(event_date, build_end).isoformat(),
                focus="Gradually extend weekend long run distance while keeping weekday efforts controlled.",
                weekly_mileage_target_km=round(baseline.baseline_weekly_km * 1.15, 1),
            )
        )
        current_phase_start = build_end + dt.timedelta(days=1)

    # Peak & Taper
    if current_phase_start < event_date:
        phases.append(
            PlanPhase(
                name="Event Readiness & Taper",
                start_date=current_phase_start.isoformat(),
                end_date=event_date.isoformat(),
                focus="Preserve neuromuscular sharpness, reduce total volume, and arrive fully recovered on event day.",
                weekly_mileage_target_km=round(baseline.baseline_weekly_km * 0.80, 1),
            )
        )

    # 5. Milestones
    milestones: list[MilestoneCheck] = [
        MilestoneCheck(
            target_date=(start_date + dt.timedelta(days=min(14, horizon_days // 2))).isoformat(),
            title="Consistency Checkpoint",
            description="Complete two consecutive weeks of planned sessions without missing priority runs.",
            criteria="100% completion of scheduled high-priority sessions.",
        ),
        MilestoneCheck(
            target_date=(event_date - dt.timedelta(days=min(7, horizon_days // 3))).isoformat(),
            title="Event Simulation & Gear Rehearsal",
            description="Complete rehearsal run in target event footwear and hydration setup.",
            criteria="Comfortable execution with zero pain flags.",
        ),
    ]

    # 6. Generate Rolling 7-Day Sessions
    seven_day_sessions: list[GeneratedSession] = []
    preferred_long_run_day = "sunday" if "sunday" in avail_days_set else ("saturday" if "saturday" in avail_days_set else list(avail_days_set)[-1])

    # Determine safe volume breakdown for week 1
    w1_target_km = baseline.baseline_weekly_km
    available_running_days = len(avail_days_set)
    easy_run_duration = min(time_cap, max(25, int(w1_target_km / available_running_days * 7.0)))
    long_run_duration = min(time_cap, int(easy_run_duration * 1.4))

    for day_offset in range(7):
        curr_date = start_date + dt.timedelta(days=day_offset)
        if curr_date > event_date:
            break

        weekday_name = WEEKDAY_NAMES[curr_date.weekday()]
        is_event_day = (curr_date == event_date)

        if is_event_day:
            # Event day workout
            session = GeneratedSession(
                local_date=curr_date.isoformat(),
                weekday=weekday_name,
                session_type="easy_run",
                purpose=f"Event Day: {event_title}",
                duration_min_min=min(time_cap, int(target_distance_km * 6.5)),
                duration_min_max=min(time_cap, int(target_distance_km * 7.5)),
                distance_unit="km",
                distance_km_min=target_distance_km,
                distance_km_max=target_distance_km,
                effort_target="Target Event Effort / Controlled Rhythm",
                blocks=[
                    PlannedWorkoutBlock(name="warmup", description="10 min light mobility & gentle jog", duration_min=10),
                    PlannedWorkoutBlock(name="main_set", description=f"{target_distance_km} km Event Run", duration_min=int(target_distance_km * 6)),
                    PlannedWorkoutBlock(name="cooldown", description="10 min easy walking & post-event recovery", duration_min=10),
                ],
                target_pace_sec_per_km=baseline.estimated_easy_pace_sec_per_km,
                priority="high",
                flexibility_window_days=0,
                reason_codes=["EVENT_DAY_SCHEDULED"],
            )
        elif weekday_name not in avail_days_set:
            # Scheduled Rest Day
            session = GeneratedSession(
                local_date=curr_date.isoformat(),
                weekday=weekday_name,
                session_type="rest",
                purpose="Rest and physiological adaptation day",
                duration_min_min=0,
                duration_min_max=0,
                distance_unit="km",
                distance_km_min=0.0,
                distance_km_max=0.0,
                effort_target="Complete Rest / Light Mobility",
                blocks=[
                    PlannedWorkoutBlock(name="main_set", description="Rest day. Hydrate, sleep well, and allow muscles to repair.", duration_min=0)
                ],
                target_pace_sec_per_km=None,
                priority="rest",
                flexibility_window_days=0,
                reason_codes=["SCHEDULED_REST_DAY"],
            )
        elif weekday_name == preferred_long_run_day:
            # Weekend Long Run
            long_km = round(min(target_distance_km * 0.75, w1_target_km * 0.38), 1)
            session = GeneratedSession(
                local_date=curr_date.isoformat(),
                weekday=weekday_name,
                session_type="long_run",
                purpose="Aerobic stamina development and endurance adaptation",
                duration_min_min=max(35, long_run_duration - 5),
                duration_min_max=min(time_cap, long_run_duration + 5),
                distance_unit="km",
                distance_km_min=max(3.0, long_km - 0.5),
                distance_km_max=max(4.0, long_km + 0.5),
                effort_target="Easy / Conversational (RPE 3-4)",
                blocks=[
                    PlannedWorkoutBlock(name="warmup", description="5-8 min dynamic mobility & walking lunges", duration_min=5),
                    PlannedWorkoutBlock(name="main_set", description=f"Continuous comfortable aerobic run (~{long_km} km)", duration_min=long_run_duration - 10),
                    PlannedWorkoutBlock(name="cooldown", description="5 min slow walking & gentle lower body stretches", duration_min=5),
                ],
                target_pace_sec_per_km=baseline.estimated_easy_pace_sec_per_km,
                priority="high",
                flexibility_window_days=1,
                reason_codes=["WEEKLY_LONG_RUN", "AEROBIC_ENDURANCE"],
            )
        else:
            # Standard Easy Aerobic Run
            easy_km = round(max(2.5, (w1_target_km - (w1_target_km * 0.38)) / max(1, available_running_days - 1)), 1)
            session = GeneratedSession(
                local_date=curr_date.isoformat(),
                weekday=weekday_name,
                session_type="easy_run",
                purpose="Aerobic base building and recovery circulation",
                duration_min_min=max(20, easy_run_duration - 5),
                duration_min_max=min(time_cap, easy_run_duration + 5),
                distance_unit="km",
                distance_km_min=max(2.0, easy_km - 0.5),
                distance_km_max=max(3.0, easy_km + 0.5),
                effort_target="Easy / Conversational (RPE 3-4)",
                blocks=[
                    PlannedWorkoutBlock(name="warmup", description="5 min brisk walking & gentle leg swings", duration_min=5),
                    PlannedWorkoutBlock(name="main_set", description=f"Easy conversation-paced run (~{easy_km} km)", duration_min=easy_run_duration - 10),
                    PlannedWorkoutBlock(name="cooldown", description="5 min light cool-down walking", duration_min=5),
                ],
                target_pace_sec_per_km=baseline.estimated_easy_pace_sec_per_km,
                priority="medium",
                flexibility_window_days=1,
                reason_codes=["AEROBIC_BASE_BUILDING", "CONVERSATIONAL_RUN"],
            )

        seven_day_sessions.append(session)

    # 7. Coach Explanation
    confidence_explanation = {
        "high": "Your plan is built from verified recent race performance and volume evidence.",
        "medium": "Your plan is tailored to your reported weekly running frequency and estimated volume.",
        "low": "Starting with an introductory conservative volume to safely establish your aerobic foundation.",
        "unknown": "Baseline was not provided; starting with a cautious introductory schedule to prioritize injury prevention.",
    }.get(baseline.confidence, "Introductory schedule.")

    explanation = (
        f"Initial training plan generated for {event_title} ({target_distance_km} km on {event_date_str}). "
        f"{confidence_explanation} "
        f"Week 1 schedules {len([s for s in seven_day_sessions if s.session_type != 'rest'])} running sessions "
        f"respecting your {time_cap}-minute daily time cap."
    )

    limitations = (
        "This plan provides conservative rule-based exercise recommendations. "
        "It is not medical advice, clinical diagnosis, or a guarantee of performance outcomes."
    )

    return GeneratedPlanOutput(
        algorithm_version=PLANNER_ALGORITHM_VERSION,
        input_snapshot_hash=snapshot_hash,
        start_date=start_date_str,
        end_date=event_date_str,
        days_until_event=horizon_days,
        phases=phases,
        milestones=milestones,
        seven_day_sessions=seven_day_sessions,
        explanation=explanation,
        trigger_reason="INITIAL_PLAN_GENERATION",
        confidence=baseline.confidence,
        limitations=limitations,
    )


def _get_sport_session_template(
    sport: str,
    event_title: str,
    time_cap: int,
    is_weekend: bool,
    demands_description: str,
) -> tuple[str, str, str, list[PlannedWorkoutBlock], str]:
    """Return tailored session type, purpose, effort target, blocks, and reason code for non-running sports."""
    s = sport.lower()
    if "cycl" in s or "bike" in s:
        if is_weekend:
            sess_type = "long_ride"
            purpose = f"Aerobic endurance ride for {event_title}"
            effort = "Zone 2 Steady Cadence (RPE 3-4)"
            blocks = [
                PlannedWorkoutBlock(name="warmup", description="10 min easy spinning at 85-90 RPM", duration_min=10),
                PlannedWorkoutBlock(name="main_set", description=f"Continuous aerobic endurance ride: {demands_description or 'Steady pace with hydration practice'}", duration_min=max(20, time_cap - 20)),
                PlannedWorkoutBlock(name="cooldown", description="10 min light cool-down spin & leg stretches", duration_min=10),
            ]
            code = "CYCLING_ENDURANCE_BUILD"
        else:
            sess_type = "tempo_ride"
            purpose = f"Pacing & cadence intervals for {event_title}"
            effort = "Moderate-High (RPE 5-7)"
            blocks = [
                PlannedWorkoutBlock(name="warmup", description="10 min progressive warm-up spin", duration_min=10),
                PlannedWorkoutBlock(name="main_set", description="Interval efforts with controlled recovery intervals", duration_min=max(15, time_cap - 20)),
                PlannedWorkoutBlock(name="cooldown", description="10 min easy spinning", duration_min=10),
            ]
            code = "CYCLING_TEMPO_PRACTICE"
    elif "swim" in s:
        sess_type = "swim_session"
        purpose = f"Technique, stroke efficiency & stamina for {event_title}"
        effort = "Moderate / Technique Focused (RPE 4-6)"
        blocks = [
            PlannedWorkoutBlock(name="warmup", description="200m easy warm-up (mix strokes + mobility)", duration_min=10),
            PlannedWorkoutBlock(name="main_set", description=f"Structured drill & pacing set: {demands_description or 'Continuous sets with 30s rest'}", duration_min=max(15, time_cap - 20)),
            PlannedWorkoutBlock(name="cooldown", description="150m easy backstroke / gentle swim & stretching", duration_min=10),
        ]
        code = "SWIMMING_ENDURANCE_DRILL"
    elif "strength" in s or "weight" in s or "powerlift" in s:
        sess_type = "strength_session"
        purpose = f"Movement quality, power & strength foundation for {event_title}"
        effort = "RPE 7-8 / 2-3 RIR (Reps in Reserve)"
        blocks = [
            PlannedWorkoutBlock(name="warmup", description="10 min joint mobility, hip openers & light warm-up sets", duration_min=10),
            PlannedWorkoutBlock(name="main_set", description=f"Primary compound lifts & accessory work: {demands_description or 'Focus on technical execution and rest intervals'}", duration_min=max(20, time_cap - 20)),
            PlannedWorkoutBlock(name="cooldown", description="10 min decompressing stretches & core stability", duration_min=10),
        ]
        code = "STRENGTH_DEVELOPMENT"
    elif "foot" in s or "cric" in s or "bask" in s or "badmin" in s or "tenn" in s or "volley" in s or "kabad" in s:
        sess_type = "match_conditioning"
        purpose = f"Agility, interval stamina & match-play simulation for {event_title}"
        effort = "Dynamic / Intermittent High Effort (RPE 6-7)"
        blocks = [
            PlannedWorkoutBlock(name="warmup", description="10 min dynamic agility drills, deceleration & multidirectional warm-up", duration_min=10),
            PlannedWorkoutBlock(name="main_set", description=f"Sport-specific drills, footwork & conditioning: {demands_description or 'High-intensity intervals with recovery periods'}", duration_min=max(15, time_cap - 20)),
            PlannedWorkoutBlock(name="cooldown", description="10 min slow jogging & full-body static stretches", duration_min=10),
        ]
        code = "SPORT_SPECIFIC_CONDITIONING"
    elif "hik" in s or "trek" in s:
        sess_type = "trek_conditioning"
        purpose = f"Incline stamina, leg endurance & pack conditioning for {event_title}"
        effort = "Sustained Aerobic (RPE 4-5)"
        blocks = [
            PlannedWorkoutBlock(name="warmup", description="10 min lower-leg mobility & ankle activations", duration_min=10),
            PlannedWorkoutBlock(name="main_set", description=f"Incline walking / stair conditioning: {demands_description or 'Weighted pack or incline walking with steady breathing'}", duration_min=max(20, time_cap - 20)),
            PlannedWorkoutBlock(name="cooldown", description="10 min calf, hamstring & hip flexor stretches", duration_min=10),
        ]
        code = "HIKING_TREK_PREPARATION"
    else:
        sess_type = "custom_practice"
        purpose = f"Conditioning & skills practice for {event_title}"
        effort = "Moderate / Technical Effort (RPE 5-6)"
        blocks = [
            PlannedWorkoutBlock(name="warmup", description="10 min full body mobility", duration_min=10),
            PlannedWorkoutBlock(name="main_set", description=f"Structured activity practice: {demands_description or 'Skill and conditioning'}", duration_min=max(15, time_cap - 20)),
            PlannedWorkoutBlock(name="cooldown", description="10 min stretch & cool down", duration_min=10),
        ]
        code = "CUSTOM_EVENT_PRACTICE"

    return sess_type, purpose, effort, blocks, code


def generate_initial_custom_event_plan(
    start_date_str: str,
    event_date_str: str,
    event_title: str,
    sport_category: str,
    demands_description: str,
    availability_days: list[str],
    daily_time_cap_min: int,
    timezone: str = "Asia/Kolkata",
) -> GeneratedPlanOutput:
    """Generate bounded, general preparation guidance for custom / non-running events."""
    start_date = dt.date.fromisoformat(start_date_str)
    event_date = dt.date.fromisoformat(event_date_str)
    horizon_days = (event_date - start_date).days

    if horizon_days <= 0:
        raise ValueError("Event date must be in the future.")

    avail_days_set = {d.strip().lower() for d in availability_days if d.strip().lower() in WEEKDAY_NAMES}
    if len(avail_days_set) < 2:
        avail_days_set = {"tuesday", "thursday", "saturday"}

    time_cap = max(20, min(180, int(daily_time_cap_min)))

    input_snapshot = {
        "start_date": start_date_str,
        "event_date": event_date_str,
        "event_title": event_title,
        "sport_category": sport_category,
        "demands_description": demands_description,
        "availability_days": sorted(list(avail_days_set)),
        "daily_time_cap_min": time_cap,
        "timezone": timezone,
        "algorithm_version": "slickfit_custom_v1",
    }
    snapshot_hash = compute_snapshot_hash(input_snapshot)

    phases = [
        PlanPhase(
            name="General Conditioning & Preparation",
            start_date=start_date_str,
            end_date=(start_date + dt.timedelta(days=max(7, horizon_days // 2))).isoformat(),
            focus=f"Build physical work capacity and practice fundamental skills for {event_title}.",
            weekly_mileage_target_km=0.0,
        ),
        PlanPhase(
            name="Specific Event Readiness",
            start_date=(start_date + dt.timedelta(days=max(8, horizon_days // 2 + 1))).isoformat(),
            end_date=event_date_str,
            focus="Refine pacing, nutrition timing, and event-specific movement patterns.",
            weekly_mileage_target_km=0.0,
        ),
    ]

    milestones = [
        MilestoneCheck(
            target_date=(start_date + dt.timedelta(days=min(7, horizon_days // 2))).isoformat(),
            title="Equipment & Routine Check",
            description="Verify all required gear, hydration, and facilities are functional.",
            criteria="Checklist 100% verified.",
        )
    ]

    seven_day_sessions: list[GeneratedSession] = []
    for day_offset in range(7):
        curr_date = start_date + dt.timedelta(days=day_offset)
        if curr_date > event_date:
            break

        weekday_name = WEEKDAY_NAMES[curr_date.weekday()]
        if weekday_name not in avail_days_set:
            session = GeneratedSession(
                local_date=curr_date.isoformat(),
                weekday=weekday_name,
                session_type="rest",
                purpose="Rest and recovery day",
                duration_min_min=0,
                duration_min_max=0,
                distance_unit="",
                distance_km_min=0.0,
                distance_km_max=0.0,
                effort_target="Complete Rest",
                blocks=[PlannedWorkoutBlock(name="main_set", description="Recovery day. Hydrate, rest, and sleep well.", duration_min=0)],
                target_pace_sec_per_km=None,
                priority="rest",
                flexibility_window_days=0,
                reason_codes=["SCHEDULED_REST_DAY"],
            )
        else:
            is_weekend = weekday_name in ("saturday", "sunday")
            sess_type, purpose, effort, blocks, code = _get_sport_session_template(
                sport=sport_category,
                event_title=event_title,
                time_cap=time_cap,
                is_weekend=is_weekend,
                demands_description=demands_description,
            )
            session = GeneratedSession(
                local_date=curr_date.isoformat(),
                weekday=weekday_name,
                session_type=sess_type,
                purpose=purpose,
                duration_min_min=max(20, time_cap - 15),
                duration_min_max=time_cap,
                distance_unit="",
                distance_km_min=None,
                distance_km_max=None,
                effort_target=effort,
                blocks=blocks,
                target_pace_sec_per_km=None,
                priority="medium",
                flexibility_window_days=1,
                reason_codes=[code, "GENERAL_CONDITIONING"],
            )
        seven_day_sessions.append(session)

    explanation = (
        f"Custom general preparation schedule created for {event_title} ({sport_category.capitalize()}). "
        f"Sessions are structured as editable conditioning and practice blocks respecting your {time_cap}-minute time cap. "
        "No sport-specific proprietary physiological model is claimed."
    )

    limitations = (
        "Custom event guidance provides general structured preparation and scheduling. "
        "It does not claim sport-specific scientific validation for non-running disciplines."
    )

    return GeneratedPlanOutput(
        algorithm_version="slickfit_custom_v1",
        input_snapshot_hash=snapshot_hash,
        start_date=start_date_str,
        end_date=event_date_str,
        days_until_event=horizon_days,
        phases=phases,
        milestones=milestones,
        seven_day_sessions=seven_day_sessions,
        explanation=explanation,
        trigger_reason="INITIAL_CUSTOM_EVENT_PLAN",
        confidence="medium",
        limitations=limitations,
    )
