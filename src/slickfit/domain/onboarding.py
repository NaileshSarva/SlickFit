"""Onboarding domain service for intake validation, persistence, and initial plan generation."""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import asdict
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models import (
    AthleteProfile,
    Availability,
    BaselineObservation,
    Event,
    NutritionProfile,
    Plan,
    PlannedSession,
    PlanRevision,
    User,
)
from .baseline import BaselineAssessment, assess_running_baseline
from .planner import (
    GeneratedPlanOutput,
    generate_initial_custom_event_plan,
    generate_initial_running_plan,
)


class OnboardingService:
    """Orchestrates onboarding intake, baseline derivation, and atomic initial plan creation."""

    @classmethod
    def complete_onboarding(
        cls,
        db: Session,
        user_id: str,
        event_data: dict[str, Any],
        baseline_data: dict[str, Any],
        availability_data: dict[str, Any],
        profile_data: Optional[dict[str, Any]] = None,
        nutrition_data: Optional[dict[str, Any]] = None,
    ) -> tuple[Event, Plan, PlanRevision, list[PlannedSession]]:
        user = db.get(User, user_id)
        if not user:
            raise ValueError("User not found.")

        # 1. Update Profile (only with explicitly provided non-empty values)
        profile = db.execute(select(AthleteProfile).where(AthleteProfile.user_id == user_id)).scalar_one_or_none()
        if not profile:
            profile = AthleteProfile(user_id=user_id)
            db.add(profile)

        if profile_data:
            if "age_band" in profile_data and profile_data["age_band"]:
                profile.age_band = str(profile_data["age_band"]).strip()
            if "sex" in profile_data and profile_data["sex"]:
                profile.sex = str(profile_data["sex"]).strip()
            if "height_cm" in profile_data and profile_data["height_cm"] is not None:
                profile.height_cm = float(profile_data["height_cm"])
            if "weight_kg" in profile_data and profile_data["weight_kg"] is not None:
                profile.weight_kg = float(profile_data["weight_kg"])
            if "region" in profile_data and profile_data["region"]:
                profile.region = str(profile_data["region"]).strip()

        # 2. Availability persistence
        training_days = availability_data.get("training_days") or ["monday", "wednesday", "friday", "saturday"]
        daily_time_cap = int(availability_data.get("daily_time_cap_min", 60))

        availability = db.execute(select(Availability).where(Availability.user_id == user_id)).scalar_one_or_none()
        if not availability:
            availability = Availability(user_id=user_id)
            db.add(availability)

        availability.training_days_json = json.dumps(training_days)
        availability.daily_time_cap_min = daily_time_cap
        if "preferred_times" in availability_data:
            availability.preferred_times_json = json.dumps(availability_data["preferred_times"])
        if "environment_equipment" in availability_data:
            availability.environment_equipment = str(availability_data["environment_equipment"])

        # 3. Nutrition preferences persistence
        if nutrition_data:
            nutrition = db.execute(select(NutritionProfile).where(NutritionProfile.user_id == user_id)).scalar_one_or_none()
            if not nutrition:
                nutrition = NutritionProfile(user_id=user_id)
                db.add(nutrition)

            if "dietary_pattern" in nutrition_data:
                nutrition.dietary_pattern = str(nutrition_data["dietary_pattern"])
            if "regional_preference" in nutrition_data:
                nutrition.regional_preference = str(nutrition_data["regional_preference"])
            if "allergies" in nutrition_data:
                nutrition.allergies_json = json.dumps(nutrition_data["allergies"])
            if "foods_avoided" in nutrition_data:
                nutrition.foods_avoided_json = json.dumps(nutrition_data["foods_avoided"])
            if "goal_preference" in nutrition_data:
                nutrition.goal_preference = str(nutrition_data["goal_preference"])

        # 4. Event persistence
        kind = event_data.get("kind", "running").strip().lower()
        title = event_data.get("title", "Goal Event").strip()
        event_date_str = event_data.get("event_date", "").strip()
        if not event_date_str:
            raise ValueError("Event date is required.")

        target_distance = float(event_data.get("target_value", 10.0) or 10.0) if kind == "running" else None
        goal_type = event_data.get("goal_type", "finish").strip().lower()

        # Archive previous active events
        prev_events = db.execute(select(Event).where(Event.user_id == user_id, Event.status == "active")).scalars().all()
        for prev in prev_events:
            prev.status = "archived"

        event = Event(
            user_id=user_id,
            kind=kind,
            sport=event_data.get("sport", "running"),
            title=title,
            event_date=event_date_str,
            timezone=user.timezone,
            location=event_data.get("location", ""),
            goal_type=goal_type,
            target_value=target_distance,
            target_unit="km" if kind == "running" else event_data.get("target_unit", ""),
            demands_json=json.dumps(event_data.get("demands", {})),
            status="active",
            notes=event_data.get("notes", ""),
        )
        db.add(event)
        db.flush()  # populate event.id

        # 5. Baseline assessment & observation records
        assessment = assess_running_baseline(
            experience_level=baseline_data.get("experience_level"),
            recent_weekly_km=baseline_data.get("recent_weekly_km"),
            recent_runs_per_week=baseline_data.get("recent_runs_per_week"),
            recent_race_distance_km=baseline_data.get("recent_race_distance_km"),
            recent_race_time_sec=baseline_data.get("recent_race_time_sec"),
            easy_pace_sec_per_km=baseline_data.get("easy_pace_sec_per_km"),
        )

        # Record baseline observation
        obs = BaselineObservation(
            user_id=user_id,
            discipline=kind,
            metric_type="experience_and_volume",
            value=assessment.baseline_weekly_km,
            unit="km/week",
            protocol="user_onboarding_intake",
            observation_date=dt.date.today().isoformat(),
            source="user_onboarding",
            confidence=assessment.confidence,
            notes=f"Experience: {assessment.experience_level}; Reasons: {', '.join(assessment.reasons)}",
        )
        db.add(obs)

        # 6. Plan generation
        start_date_str = dt.date.today().isoformat()
        if kind == "running":
            plan_output = generate_initial_running_plan(
                start_date_str=start_date_str,
                event_date_str=event_date_str,
                event_title=title,
                target_distance_km=target_distance or 10.0,
                goal_type=goal_type,
                availability_days=training_days,
                daily_time_cap_min=daily_time_cap,
                baseline=assessment,
                timezone=user.timezone,
            )
        else:
            plan_output = generate_initial_custom_event_plan(
                start_date_str=start_date_str,
                event_date_str=event_date_str,
                event_title=title,
                sport_category=event_data.get("sport", "custom_event"),
                demands_description=str(event_data.get("demands", {}).get("description", "")),
                availability_days=training_days,
                daily_time_cap_min=daily_time_cap,
                timezone=user.timezone,
            )

        # Archive previous plans
        prev_plans = db.execute(select(Plan).where(Plan.user_id == user_id, Plan.status == "active")).scalars().all()
        for p in prev_plans:
            p.status = "archived"

        plan = Plan(
            user_id=user_id,
            event_id=event.id,
            algorithm_version=plan_output.algorithm_version,
            status="active",
        )
        db.add(plan)
        db.flush()

        plan_rev = PlanRevision(
            plan_id=plan.id,
            user_id=user_id,
            revision_number=1,
            input_snapshot_hash=plan_output.input_snapshot_hash,
            start_date=plan_output.start_date,
            end_date=plan_output.end_date,
            phases_json=json.dumps([asdict(p) for p in plan_output.phases]),
            status="current",
            explanation=plan_output.explanation,
            trigger_reason=plan_output.trigger_reason,
        )
        db.add(plan_rev)
        db.flush()

        sessions: list[PlannedSession] = []
        for s in plan_output.seven_day_sessions:
            sess_model = PlannedSession(
                plan_revision_id=plan_rev.id,
                user_id=user_id,
                local_date=s.local_date,
                session_type=s.session_type,
                purpose=s.purpose,
                duration_min_min=s.duration_min_min,
                duration_min_max=s.duration_min_max,
                distance_km_min=s.distance_km_min,
                distance_km_max=s.distance_km_max,
                effort_target=s.effort_target,
                blocks_json=json.dumps([asdict(b) for b in s.blocks]),
                target_pace_sec_per_km=s.target_pace_sec_per_km,
                priority=s.priority,
                flexibility_window_days=s.flexibility_window_days,
                status="scheduled",
                reason_codes_json=json.dumps(s.reason_codes),
            )
            db.add(sess_model)
            sessions.append(sess_model)

        db.commit()
        db.refresh(event)
        db.refresh(plan)
        db.refresh(plan_rev)

        return event, plan, plan_rev, sessions
