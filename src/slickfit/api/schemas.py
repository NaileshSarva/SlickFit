"""Pydantic schemas and DTOs for API validation and response shaping."""

from __future__ import annotations

import datetime as dt
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class ErrorDetail(BaseModel):
    loc: list[str] = Field(default_factory=list)
    msg: str
    type: str = "value_error"


class ErrorResponse(BaseModel):
    code: str
    message: str
    field_errors: list[ErrorDetail] = Field(default_factory=list)
    request_id: str = ""


# -- Auth & User Schemas ---------------------------------------------
class RegisterRequest(BaseModel):
    email: str = Field(pattern=EMAIL_PATTERN, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(default="", max_length=128)
    timezone: str = Field(default="Asia/Kolkata", max_length=64)
    locale: str = Field(default="en-IN", max_length=32)
    units: str = Field(default="metric", max_length=16)


class LoginRequest(BaseModel):
    email: str = Field(pattern=EMAIL_PATTERN, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class DemoLoginRequest(BaseModel):
    demo_key: str = Field(default="demo1", pattern="^(demo1|demo2)$")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    is_demo: bool


class AthleteProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    age_band: str
    sex: str
    height_cm: Optional[float]
    weight_kg: Optional[float]
    region: str
    updated_at: dt.datetime


class AvailabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    training_days_json: str
    daily_time_cap_min: int
    preferred_times_json: str
    environment_equipment: str
    unavailable_dates_json: str
    updated_at: dt.datetime


class NutritionProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dietary_pattern: str
    regional_preference: str
    allergies_json: str
    foods_avoided_json: str
    goal_preference: str
    intake_target_kcal: Optional[int]
    updated_at: dt.datetime


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    is_active: bool
    is_demo: bool
    timezone: str
    locale: str
    units: str
    created_at: dt.datetime
    profile: Optional[AthleteProfileResponse] = None
    availability: Optional[AvailabilityResponse] = None
    nutrition_profile: Optional[NutritionProfileResponse] = None


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=128)
    timezone: Optional[str] = Field(default=None, max_length=64)
    locale: Optional[str] = Field(default=None, max_length=32)
    units: Optional[str] = Field(default=None, max_length=16)


# -- Event Schemas ----------------------------------------------------
class EventCreateRequest(BaseModel):
    kind: str = Field(default="running", pattern="^(running|custom)$")
    sport: str = Field(default="running", max_length=64)
    title: str = Field(min_length=2, max_length=255)
    event_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    location: str = Field(default="", max_length=255)
    goal_type: str = Field(default="finish", pattern="^(finish|build_capacity|target_time)$")
    target_value: Optional[float] = Field(default=None, gt=0)
    target_unit: str = Field(default="km", max_length=32)
    demands: dict[str, Any] = Field(default_factory=dict)
    notes: str = Field(default="", max_length=1000)


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    kind: str
    sport: str
    title: str
    event_date: str
    timezone: str
    location: str
    goal_type: str
    target_value: Optional[float]
    target_unit: str
    demands_json: str
    status: str
    notes: str
    created_at: dt.datetime
    updated_at: dt.datetime


# -- Onboarding Intake Schemas ----------------------------------------
class BaselineIntakeRequest(BaseModel):
    experience_level: Optional[str] = Field(default=None, max_length=32)
    recent_weekly_km: Optional[float] = Field(default=None, ge=0, le=300)
    recent_runs_per_week: Optional[int] = Field(default=None, ge=0, le=7)
    recent_race_distance_km: Optional[float] = Field(default=None, gt=0, le=100)
    recent_race_time_sec: Optional[int] = Field(default=None, gt=0, le=86400)
    easy_pace_sec_per_km: Optional[int] = Field(default=None, ge=180, le=720)


class AvailabilityIntakeRequest(BaseModel):
    training_days: list[str] = Field(default_factory=lambda: ["monday", "wednesday", "friday", "saturday"])
    daily_time_cap_min: int = Field(default=60, ge=20, le=180)
    preferred_times: list[str] = Field(default_factory=lambda: ["morning"])
    environment_equipment: str = Field(default="road_outdoor", max_length=255)


class ProfileIntakeRequest(BaseModel):
    age_band: Optional[str] = Field(default=None, max_length=32)
    sex: Optional[str] = Field(default=None, max_length=32)
    height_cm: Optional[float] = Field(default=None, ge=100, le=250)
    weight_kg: Optional[float] = Field(default=None, ge=30, le=250)
    region: Optional[str] = Field(default=None, max_length=128)


class NutritionIntakeRequest(BaseModel):
    dietary_pattern: str = Field(default="vegetarian", max_length=64)
    regional_preference: str = Field(default="south_indian", max_length=64)
    allergies: list[str] = Field(default_factory=list)
    foods_avoided: list[str] = Field(default_factory=list)
    goal_preference: str = Field(default="endurance_fueling", max_length=64)


class OnboardingRequest(BaseModel):
    event: EventCreateRequest
    baseline: BaselineIntakeRequest = Field(default_factory=BaselineIntakeRequest)
    availability: AvailabilityIntakeRequest = Field(default_factory=AvailabilityIntakeRequest)
    profile: Optional[ProfileIntakeRequest] = None
    nutrition: Optional[NutritionIntakeRequest] = None


class PlannedSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    plan_revision_id: str
    local_date: str
    session_type: str
    purpose: str
    duration_min_min: int
    duration_min_max: int
    distance_km_min: Optional[float]
    distance_km_max: Optional[float]
    effort_target: str
    blocks_json: str
    target_pace_sec_per_km: Optional[int]
    priority: str
    flexibility_window_days: int
    status: str
    reason_codes_json: str
    created_at: dt.datetime


class PlanRevisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    plan_id: str
    revision_number: int
    input_snapshot_hash: str
    start_date: str
    end_date: str
    phases_json: str
    status: str
    explanation: str
    trigger_reason: str
    created_at: dt.datetime


class PlanDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_id: str
    event_title: str
    event_date: str
    days_until_event: int
    algorithm_version: str
    status: str
    current_revision: PlanRevisionResponse
    sessions: list[PlannedSessionResponse]
    confidence: str
    created_at: dt.datetime


class OnboardingResponse(BaseModel):
    message: str
    event: EventResponse
    plan: PlanDetailResponse


# -- Activity Logging Schemas -----------------------------------------
class ActivityCreateRequest(BaseModel):
    planned_session_id: Optional[str] = None
    local_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    activity_type: str = Field(default="running", max_length=64)
    duration_min: float = Field(ge=0, le=600)
    distance_km: Optional[float] = Field(default=None, ge=0, le=200)
    perceived_effort: int = Field(default=5, ge=1, le=10)
    completion_state: str = Field(default="completed", pattern="^(completed|partial|skipped)$")
    early_stop_reason: str = Field(default="", max_length=64)
    pain_flag: bool = False
    pain_notes: str = Field(default="", max_length=500)
    notes: str = Field(default="", max_length=1000)


class ActivityUpdateRequest(BaseModel):
    duration_min: Optional[float] = Field(default=None, ge=0, le=600)
    distance_km: Optional[float] = Field(default=None, ge=0, le=200)
    perceived_effort: Optional[int] = Field(default=None, ge=1, le=10)
    completion_state: Optional[str] = Field(default=None, pattern="^(completed|partial|skipped)$")
    notes: Optional[str] = Field(default=None, max_length=1000)
    change_reason: str = Field(min_length=3, max_length=500)


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    planned_session_id: Optional[str]
    local_date: str
    timezone: str
    activity_type: str
    duration_min: float
    distance_km: Optional[float]
    perceived_effort: int
    completion_state: str
    early_stop_reason: str
    pain_flag: bool
    pain_notes: str
    notes: str
    source: str
    confidence: str
    is_manual: bool
    created_at: dt.datetime
    updated_at: dt.datetime


# -- Daily Check-In Schemas -------------------------------------------
class DailyCheckInCreateRequest(BaseModel):
    local_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    sleep_duration_hours: Optional[float] = Field(default=None, ge=0, le=24)
    sleep_quality: int = Field(default=3, ge=1, le=5)
    energy_level: int = Field(default=3, ge=1, le=5)
    soreness_level: int = Field(default=1, ge=1, le=5)
    stress_level: int = Field(default=2, ge=1, le=5)
    pain_flag: bool = False
    pain_area: str = Field(default="", max_length=128)
    pain_severity: int = Field(default=0, ge=0, le=10)
    red_flag_symptom: bool = False
    notes: str = Field(default="", max_length=500)


class DailyCheckInResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    local_date: str
    checkin_time_utc: dt.datetime
    sleep_duration_hours: Optional[float]
    sleep_quality: int
    energy_level: int
    soreness_level: int
    stress_level: int
    pain_flag: bool
    pain_area: str
    pain_severity: int
    red_flag_symptom: bool
    notes: str
    source: str
    created_at: dt.datetime


# -- Nutrition Guidance Schemas ---------------------------------------
class NutritionGuidanceResponse(BaseModel):
    local_date: str
    dietary_pattern: str
    regional_preference: str
    min_kcal: int
    max_kcal: int
    protein_g_min: int
    protein_g_max: int
    carbs_g_min: int
    carbs_g_max: int
    fats_g_min: int
    fats_g_max: int
    hydration_liters: float
    meal_ideas: list[dict[str, Any]]
    rationale: str
    limitations: str


# -- History & Amendment Schemas --------------------------------------
class DataAmendmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    entity_type: str
    entity_id: str
    field_name: str
    prior_value: str
    replacement_value: str
    actor_user_id: str
    reason: str
    source: str
    created_at: dt.datetime


class HistoryFeedItem(BaseModel):
    id: str
    item_type: str  # "activity" | "checkin" | "adaptation" | "amendment"
    local_date: str
    timestamp: dt.datetime
    title: str
    summary: str
    metrics: dict[str, Any] = Field(default_factory=dict)
    details: dict[str, Any] = Field(default_factory=dict)


class ProgressTrendResponse(BaseModel):
    total_runs_completed: int
    total_distance_km: float
    total_duration_min: float
    consistency_rate_pct: float
    recent_runs: list[dict[str, Any]]
    weekly_mileage_series: list[dict[str, Any]]
