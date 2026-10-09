"""Normalized SQLAlchemy domain and persistence models for SlickFit."""

from __future__ import annotations

import datetime as dt
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, generate_uuid, utc_now


class User(Base):
    """Authenticated user / athlete principal."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata", nullable=False)
    locale: Mapped[str] = mapped_column(String(32), default="en-IN", nullable=False)
    units: Mapped[str] = mapped_column(String(16), default="metric", nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    # Relationships
    profile: Mapped[Optional["AthleteProfile"]] = relationship(
        "AthleteProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    events: Mapped[list["Event"]] = relationship(
        "Event", back_populates="user", cascade="all, delete-orphan"
    )
    availability: Mapped[Optional["Availability"]] = relationship(
        "Availability", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    baseline_observations: Mapped[list["BaselineObservation"]] = relationship(
        "BaselineObservation", back_populates="user", cascade="all, delete-orphan"
    )
    plans: Mapped[list["Plan"]] = relationship(
        "Plan", back_populates="user", cascade="all, delete-orphan"
    )
    activities: Mapped[list["Activity"]] = relationship(
        "Activity", back_populates="user", cascade="all, delete-orphan"
    )
    checkins: Mapped[list["DailyCheckIn"]] = relationship(
        "DailyCheckIn", back_populates="user", cascade="all, delete-orphan"
    )
    nutrition_profile: Mapped[Optional["NutritionProfile"]] = relationship(
        "NutritionProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    nutrition_guidance: Mapped[list["NutritionGuidance"]] = relationship(
        "NutritionGuidance", back_populates="user", cascade="all, delete-orphan"
    )
    amendments: Mapped[list["DataAmendment"]] = relationship(
        "DataAmendment", back_populates="user", cascade="all, delete-orphan"
    )


class AthleteProfile(Base):
    """Athlete physical and demographic attributes."""

    __tablename__ = "athlete_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    age_band: Mapped[str] = mapped_column(String(32), default="", nullable=False)  # e.g., "18-29", "30-39", etc.
    sex: Mapped[str] = mapped_column(String(32), default="", nullable=False)  # optional
    height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    region: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="profile")


class Event(Base):
    """Target sports or fitness event."""

    __tablename__ = "events"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    kind: Mapped[str] = mapped_column(String(32), default="running", nullable=False)  # running | custom
    sport: Mapped[str] = mapped_column(String(64), default="running", nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    event_date: Mapped[str] = mapped_column(String(32), nullable=False)  # YYYY-MM-DD local date
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata", nullable=False)
    location: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    goal_type: Mapped[str] = mapped_column(
        String(32), default="finish", nullable=False
    )  # finish | build_capacity | target_time
    target_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # e.g. target seconds or km
    target_unit: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    demands_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default="active", nullable=False
    )  # active | completed | cancelled
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="events")
    plans: Mapped[list["Plan"]] = relationship(
        "Plan", back_populates="event", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_events_user_status", "user_id", "status"),
    )


class Availability(Base):
    """Athlete schedule constraints and training availability."""

    __tablename__ = "availabilities"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    training_days_json: Mapped[str] = mapped_column(
        Text, default='["monday","tuesday","thursday","saturday","sunday"]', nullable=False
    )
    daily_time_cap_min: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    preferred_times_json: Mapped[str] = mapped_column(Text, default='["morning"]', nullable=False)
    environment_equipment: Mapped[str] = mapped_column(String(255), default="road_outdoor", nullable=False)
    unavailable_dates_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="availability")


class BaselineObservation(Base):
    """Observable fitness baselines and experience markers (with unknown support)."""

    __tablename__ = "baseline_observations"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    discipline: Mapped[str] = mapped_column(String(64), default="running", nullable=False)
    metric_type: Mapped[str] = mapped_column(
        String(64), default="weekly_volume", nullable=False
    )  # weekly_volume | recent_race | easy_pace | experience_level
    value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    protocol: Mapped[str] = mapped_column(String(128), default="self_reported", nullable=False)
    observation_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="user_onboarding", nullable=False)
    confidence: Mapped[str] = mapped_column(
        String(32), default="medium", nullable=False
    )  # low | medium | high | unknown
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    is_amended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="baseline_observations")

    __table_args__ = (
        Index("ix_baseline_user_metric", "user_id", "metric_type"),
    )


class Plan(Base):
    """High-level training plan container attached to an active event."""

    __tablename__ = "plans"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("events.id", ondelete="CASCADE"), index=True, nullable=False
    )
    algorithm_version: Mapped[str] = mapped_column(String(32), default="slickfit_v1_rules", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)  # active | archived
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="plans")
    event: Mapped["Event"] = relationship("Event", back_populates="plans")
    revisions: Mapped[list["PlanRevision"]] = relationship(
        "PlanRevision", back_populates="plan", cascade="all, delete-orphan", order_by="PlanRevision.revision_number"
    )
    adaptation_events: Mapped[list["AdaptationEvent"]] = relationship(
        "AdaptationEvent", back_populates="plan", cascade="all, delete-orphan"
    )


class PlanRevision(Base):
    """Immutable revision snapshot of a training plan."""

    __tablename__ = "plan_revisions"

    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("plans.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    input_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    start_date: Mapped[str] = mapped_column(String(32), nullable=False)  # YYYY-MM-DD
    end_date: Mapped[str] = mapped_column(String(32), nullable=False)  # YYYY-MM-DD
    phases_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="current", nullable=False)  # current | superseded
    explanation: Mapped[str] = mapped_column(Text, default="", nullable=False)
    trigger_reason: Mapped[str] = mapped_column(String(64), default="initial_generation", nullable=False)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="revisions")
    sessions: Mapped[list["PlannedSession"]] = relationship(
        "PlannedSession", back_populates="revision", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_plan_rev_unique", "plan_id", "revision_number", unique=True),
        Index("ix_plan_rev_user_status", "user_id", "status"),
    )


class PlannedSession(Base):
    """Prescribed workout session in a specific plan revision."""

    __tablename__ = "planned_sessions"

    plan_revision_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("plan_revisions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    local_date: Mapped[str] = mapped_column(String(32), index=True, nullable=False)  # YYYY-MM-DD
    session_type: Mapped[str] = mapped_column(
        String(64), default="easy_run", nullable=False
    )  # easy_run | long_run | tempo | intervals | rest | recovery_walk | custom_practice
    purpose: Mapped[str] = mapped_column(Text, default="", nullable=False)
    duration_min_min: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    duration_min_max: Mapped[int] = mapped_column(Integer, default=45, nullable=False)
    distance_unit: Mapped[str] = mapped_column(String(16), default="km", nullable=False)
    distance_km_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    distance_km_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    effort_target: Mapped[str] = mapped_column(
        String(64), default="Easy / Conversational (RPE 3-4)", nullable=False
    )
    blocks_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)  # warmup, main, cooldown blocks
    target_pace_sec_per_km: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    priority: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)  # high | medium | low | rest
    flexibility_window_days: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default="scheduled", nullable=False
    )  # scheduled | completed | skipped | dropped
    reason_codes_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)

    revision: Mapped["PlanRevision"] = relationship("PlanRevision", back_populates="sessions")
    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="planned_session")

    __table_args__ = (
        Index("ix_planned_sessions_user_date", "user_id", "local_date"),
    )


class Activity(Base):
    """Logged actual workout or training execution."""

    __tablename__ = "activities"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    planned_session_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("planned_sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    local_date: Mapped[str] = mapped_column(String(32), index=True, nullable=False)  # YYYY-MM-DD
    start_time_utc: Mapped[Optional[dt.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata", nullable=False)
    activity_type: Mapped[str] = mapped_column(String(64), default="running", nullable=False)
    duration_min: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    distance_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    perceived_effort: Mapped[int] = mapped_column(Integer, default=5, nullable=False)  # RPE 1-10
    completion_state: Mapped[str] = mapped_column(
        String(32), default="completed", nullable=False
    )  # completed | partial | skipped
    early_stop_reason: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    pain_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pain_notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    source: Mapped[str] = mapped_column(String(64), default="manual", nullable=False)
    confidence: Mapped[str] = mapped_column(String(32), default="high", nullable=False)
    is_manual: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="activities")
    planned_session: Mapped[Optional["PlannedSession"]] = relationship("PlannedSession", back_populates="activities")
    revisions: Mapped[list["ActivityRevision"]] = relationship(
        "ActivityRevision", back_populates="activity", cascade="all, delete-orphan", order_by="ActivityRevision.revision_number"
    )

    __table_args__ = (
        Index("ix_activities_user_date", "user_id", "local_date"),
    )


class ActivityRevision(Base):
    """Audit revision record for edited activity data."""

    __tablename__ = "activity_revisions"

    activity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("activities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_min: Mapped[float] = mapped_column(Float, nullable=False)
    distance_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    perceived_effort: Mapped[int] = mapped_column(Integer, nullable=False)
    completion_state: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    change_reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    changed_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    activity: Mapped["Activity"] = relationship("Activity", back_populates="revisions")

    __table_args__ = (
        Index("ix_act_rev_unique", "activity_id", "revision_number", unique=True),
    )


class DailyCheckIn(Base):
    """Daily subjective recovery and wellness log."""

    __tablename__ = "daily_checkins"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    local_date: Mapped[str] = mapped_column(String(32), index=True, nullable=False)  # YYYY-MM-DD
    checkin_time_utc: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    sleep_duration_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sleep_quality: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # 1-5 scale
    energy_level: Mapped[int] = mapped_column(Integer, default=3, nullable=False)   # 1-5 scale
    soreness_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False) # 1-5 scale (1=none, 5=severe)
    stress_level: Mapped[int] = mapped_column(Integer, default=2, nullable=False)   # 1-5 scale
    pain_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pain_area: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    pain_severity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-10
    red_flag_symptom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    source: Mapped[str] = mapped_column(String(64), default="app_home", nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="checkins")

    __table_args__ = (
        Index("ix_checkins_user_date", "user_id", "local_date"),
    )


class NutritionProfile(Base):
    """Dietary preferences, regional variations, and allergy exclusions."""

    __tablename__ = "nutrition_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    dietary_pattern: Mapped[str] = mapped_column(
        String(64), default="vegetarian", nullable=False
    )  # vegetarian | eggetarian | non_vegetarian | vegan | jain
    regional_preference: Mapped[str] = mapped_column(
        String(64), default="south_indian", nullable=False
    )  # south_indian | north_indian | west_indian | east_indian | pan_indian
    allergies_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    foods_avoided_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    goal_preference: Mapped[str] = mapped_column(
        String(64), default="endurance_fueling", nullable=False
    )
    intake_target_kcal: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    activity_level: Mapped[str] = mapped_column(String(64), default="moderate", nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="nutrition_profile")


class NutritionGuidance(Base):
    """Daily estimated fuel and hydration suggestions with limitations."""

    __tablename__ = "nutrition_guidance"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    local_date: Mapped[str] = mapped_column(String(32), index=True, nullable=False)  # YYYY-MM-DD
    min_kcal: Mapped[int] = mapped_column(Integer, nullable=False)
    max_kcal: Mapped[int] = mapped_column(Integer, nullable=False)
    protein_g_min: Mapped[int] = mapped_column(Integer, nullable=False)
    protein_g_max: Mapped[int] = mapped_column(Integer, nullable=False)
    carbs_g_min: Mapped[int] = mapped_column(Integer, nullable=False)
    carbs_g_max: Mapped[int] = mapped_column(Integer, nullable=False)
    fats_g_min: Mapped[int] = mapped_column(Integer, nullable=False)
    fats_g_max: Mapped[int] = mapped_column(Integer, nullable=False)
    hydration_liters: Mapped[float] = mapped_column(Float, default=3.0, nullable=False)
    meal_ideas_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    rationale: Mapped[str] = mapped_column(Text, default="", nullable=False)
    algorithm_version: Mapped[str] = mapped_column(String(32), default="slickfit_nut_v1", nullable=False)
    confidence: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)
    limitations: Mapped[str] = mapped_column(
        Text,
        default="Estimated general guidance only. Not medical or clinical nutrition advice.",
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="nutrition_guidance")

    __table_args__ = (
        Index("ix_nut_guidance_user_date", "user_id", "local_date"),
    )


class DataAmendment(Base):
    """Immutable audit trail for user data corrections."""

    __tablename__ = "data_amendments"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)  # activity | checkin | baseline | event
    entity_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    field_name: Mapped[str] = mapped_column(String(64), nullable=False)
    prior_value: Mapped[str] = mapped_column(Text, default="", nullable=False)
    replacement_value: Mapped[str] = mapped_column(Text, default="", nullable=False)
    actor_user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    source: Mapped[str] = mapped_column(String(64), default="user_correction", nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="amendments")

    __table_args__ = (
        Index("ix_amendments_user_entity", "user_id", "entity_type", "entity_id"),
    )


class AdaptationEvent(Base):
    """Reasoned event recorded whenever the adaptive planner modifies a plan."""

    __tablename__ = "adaptation_events"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("plans.id", ondelete="CASCADE"), index=True, nullable=False
    )
    prior_plan_revision_id: Mapped[str] = mapped_column(String(36), nullable=False)
    new_plan_revision_id: Mapped[str] = mapped_column(String(36), nullable=False)
    trigger_inputs_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    reason_codes_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    explanation: Mapped[str] = mapped_column(Text, default="", nullable=False)
    algorithm_version: Mapped[str] = mapped_column(String(32), default="slickfit_v1_rules", nullable=False)
    user_visible_impact: Mapped[str] = mapped_column(Text, default="", nullable=False)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="adaptation_events")

    __table_args__ = (
        Index("ix_adaptations_user_plan", "user_id", "plan_id"),
    )
