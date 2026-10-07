"""Pydantic schemas and DTOs for API validation and response shaping."""

from __future__ import annotations

import datetime as dt
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

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
    kind: str = Field(default="running", max_length=64)
    sport: str = Field(default="running", max_length=64)
    title: str = Field(min_length=2, max_length=255)
    event_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    location: str = Field(default="", max_length=255)
    goal_type: str = Field(default="finish", max_length=64)
    target_value: Optional[float] = Field(default=None, ge=0)
    target_unit: str = Field(default="km", max_length=32)
    demands: dict[str, Any] = Field(default_factory=dict)
    notes: str = Field(default="", max_length=1000)

    @field_validator("target_value", mode="before")
    @classmethod
    def coerce_target_value(cls, v: Any) -> Optional[float]:
        if v is None or v == "" or v == "null":
            return None
        return float(v)

    @field_validator("kind", "sport", "goal_type", mode="before")
    @classmethod
    def sanitize_event_strings(cls, v: Any) -> str:
        if v is None or not str(v).strip():
            return "running"
        return str(v).strip().lower()


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
    recent_weekly_km: Optional[float] = Field(default=None, ge=0, le=500)
    recent_runs_per_week: Optional[int] = Field(default=None, ge=0, le=14)
    recent_race_distance_km: Optional[float] = Field(default=None, gt=0, le=300)
    recent_race_time_sec: Optional[int] = Field(default=None, gt=0, le=864000)
    easy_pace_sec_per_km: Optional[int] = Field(default=None, ge=120, le=1800)

    @field_validator("*", mode="before")
    @classmethod
    def coerce_empty_to_none(cls, v: Any) -> Any:
        if v == "" or v == "null":
            return None
        return v


class AvailabilityIntakeRequest(BaseModel):
    training_days: list[str] = Field(default_factory=lambda: ["monday", "wednesday", "friday", "saturday"])
    daily_time_cap_min: int = Field(default=60, ge=15, le=360)
    preferred_times: list[str] = Field(default_factory=lambda: ["morning"])
    environment_equipment: str = Field(default="road_outdoor", max_length=255)

    @field_validator("training_days", mode="before")
    @classmethod
    def normalize_training_days(cls, v: Any) -> list[str]:
        if not v:
            return ["monday", "wednesday", "friday", "saturday"]
        if isinstance(v, str):
            v = [item.strip() for item in v.split(",") if item.strip()]
        return [str(d).strip().lower() for d in v if str(d).strip()]


class ProfileIntakeRequest(BaseModel):
    age_band: Optional[str] = Field(default=None, max_length=32)
    sex: Optional[str] = Field(default=None, max_length=32)
    height_cm: Optional[float] = Field(default=None, ge=50, le=280)
    weight_kg: Optional[float] = Field(default=None, ge=20, le=350)
    region: Optional[str] = Field(default=None, max_length=128)

    @field_validator("*", mode="before")
    @classmethod
    def coerce_empty_profile_fields(cls, v: Any) -> Any:
        if v == "" or v == "null":
            return None
        return v


class NutritionIntakeRequest(BaseModel):
    dietary_pattern: str = Field(default="vegetarian", max_length=64)
    regional_preference: str = Field(default="south_indian", max_length=64)
    allergies: list[str] = Field(default_factory=list)
    foods_avoided: list[str] = Field(default_factory=list)
    goal_preference: str = Field(default="endurance_fueling", max_length=64)
    intake_target_kcal: Optional[int] = Field(default=None, ge=500, le=10000)
    activity_level: Optional[str] = Field(default=None, max_length=64)

    @field_validator("allergies", "foods_avoided", mode="before")
    @classmethod
    def sanitize_exclusion_lists(cls, v: Any) -> list[str]:
        if not v:
            return []
        if isinstance(v, str):
            v = [x.strip() for x in v.split(",") if x.strip()]
        return [str(item).strip().lower() for item in v if str(item).strip() and str(item).strip().lower() not in ("none", "null", "nil")]

    @field_validator("intake_target_kcal", mode="before")
    @classmethod
    def coerce_kcal(cls, v: Any) -> Optional[int]:
        if v == "" or v is None or v == "null":
            return None
        return int(v)

    @field_validator("dietary_pattern", "regional_preference", "goal_preference", mode="before")
    @classmethod
    def sanitize_nutrition_strings(cls, v: Any) -> str:
        if not v or not str(v).strip():
            return "default"
        return str(v).strip().lower()


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

    @field_validator("distance_km", "duration_min", mode="before")
    @classmethod
    def coerce_activity_numeric(cls, v: Any) -> Any:
        if v == "" or v == "null":
            return None
        return v


class ActivityUpdateRequest(BaseModel):
    duration_min: Optional[float] = Field(default=None, ge=0, le=600)
    distance_km: Optional[float] = Field(default=None, ge=0, le=200)
    perceived_effort: Optional[int] = Field(default=None, ge=1, le=10)
    completion_state: Optional[str] = Field(default=None, pattern="^(completed|partial|skipped)$")
    notes: Optional[str] = Field(default=None, max_length=1000)
    change_reason: str = Field(min_length=3, max_length=500)

    @field_validator("distance_km", "duration_min", "perceived_effort", mode="before")
    @classmethod
    def coerce_update_numeric(cls, v: Any) -> Any:
        if v == "" or v == "null":
            return None
        return v


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

    @field_validator("sleep_duration_hours", mode="before")
    @classmethod
    def coerce_sleep_duration(cls, v: Any) -> Optional[float]:
        if v == "" or v == "null" or v is None:
            return None
        return float(v)


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
