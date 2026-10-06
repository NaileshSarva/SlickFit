"""Initial database schema for SlickFit.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="Asia/Kolkata"),
        sa.Column("locale", sa.String(32), nullable=False, server_default="en-IN"),
        sa.Column("units", sa.String(16), nullable=False, server_default="metric"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 2. athlete_profiles
    op.create_table(
        "athlete_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("age_band", sa.String(32), nullable=False, server_default=""),
        sa.Column("sex", sa.String(32), nullable=False, server_default=""),
        sa.Column("height_cm", sa.Float(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("region", sa.String(128), nullable=False, server_default="South Asia"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_athlete_profiles_id", "athlete_profiles", ["id"])
    op.create_index("ix_athlete_profiles_user_id", "athlete_profiles", ["user_id"], unique=True)

    # 3. events
    op.create_table(
        "events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False, server_default="running"),
        sa.Column("sport", sa.String(64), nullable=False, server_default="running"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("event_date", sa.String(32), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="Asia/Kolkata"),
        sa.Column("location", sa.String(255), nullable=False, server_default=""),
        sa.Column("goal_type", sa.String(32), nullable=False, server_default="finish"),
        sa.Column("target_value", sa.Float(), nullable=True),
        sa.Column("target_unit", sa.String(32), nullable=False, server_default=""),
        sa.Column("demands_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_events_id", "events", ["id"])
    op.create_index("ix_events_user_id", "events", ["user_id"])
    op.create_index("ix_events_user_status", "events", ["user_id", "status"])

    # 4. availabilities
    op.create_table(
        "availabilities",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("training_days_json", sa.Text(), nullable=False),
        sa.Column("daily_time_cap_min", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("preferred_times_json", sa.Text(), nullable=False),
        sa.Column("environment_equipment", sa.String(255), nullable=False, server_default="road_outdoor"),
        sa.Column("unavailable_dates_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_availabilities_id", "availabilities", ["id"])
    op.create_index("ix_availabilities_user_id", "availabilities", ["user_id"], unique=True)

    # 5. baseline_observations
    op.create_table(
        "baseline_observations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("discipline", sa.String(64), nullable=False, server_default="running"),
        sa.Column("metric_type", sa.String(64), nullable=False, server_default="weekly_volume"),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(32), nullable=False, server_default=""),
        sa.Column("protocol", sa.String(128), nullable=False, server_default="self_reported"),
        sa.Column("observation_date", sa.String(32), nullable=True),
        sa.Column("source", sa.String(64), nullable=False, server_default="user_onboarding"),
        sa.Column("confidence", sa.String(32), nullable=False, server_default="medium"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("is_amended", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_baseline_observations_id", "baseline_observations", ["id"])
    op.create_index("ix_baseline_observations_user_id", "baseline_observations", ["user_id"])
    op.create_index("ix_baseline_user_metric", "baseline_observations", ["user_id", "metric_type"])

    # 6. plans
    op.create_table(
        "plans",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("algorithm_version", sa.String(32), nullable=False, server_default="slickfit_v1_rules"),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_plans_id", "plans", ["id"])
    op.create_index("ix_plans_user_id", "plans", ["user_id"])
    op.create_index("ix_plans_event_id", "plans", ["event_id"])

    # 7. plan_revisions
    op.create_table(
        "plan_revisions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("plan_id", sa.String(36), sa.ForeignKey("plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("input_snapshot_hash", sa.String(64), nullable=False),
        sa.Column("start_date", sa.String(32), nullable=False),
        sa.Column("end_date", sa.String(32), nullable=False),
        sa.Column("phases_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(32), nullable=False, server_default="current"),
        sa.Column("explanation", sa.Text(), nullable=False, server_default=""),
        sa.Column("trigger_reason", sa.String(64), nullable=False, server_default="initial_generation"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_plan_revisions_id", "plan_revisions", ["id"])
    op.create_index("ix_plan_revisions_plan_id", "plan_revisions", ["plan_id"])
    op.create_index("ix_plan_revisions_user_id", "plan_revisions", ["user_id"])
    op.create_index("ix_plan_rev_unique", "plan_revisions", ["plan_id", "revision_number"], unique=True)
    op.create_index("ix_plan_rev_user_status", "plan_revisions", ["user_id", "status"])

    # 8. planned_sessions
    op.create_table(
        "planned_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("plan_revision_id", sa.String(36), sa.ForeignKey("plan_revisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("local_date", sa.String(32), nullable=False),
        sa.Column("session_type", sa.String(64), nullable=False, server_default="easy_run"),
        sa.Column("purpose", sa.Text(), nullable=False, server_default=""),
        sa.Column("duration_min_min", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("duration_min_max", sa.Integer(), nullable=False, server_default="45"),
        sa.Column("distance_km_min", sa.Float(), nullable=True),
        sa.Column("distance_km_max", sa.Float(), nullable=True),
        sa.Column("effort_target", sa.String(64), nullable=False, server_default="Easy / Conversational (RPE 3-4)"),
        sa.Column("blocks_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("target_pace_sec_per_km", sa.Integer(), nullable=True),
        sa.Column("priority", sa.String(32), nullable=False, server_default="medium"),
        sa.Column("flexibility_window_days", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(32), nullable=False, server_default="scheduled"),
        sa.Column("reason_codes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_planned_sessions_id", "planned_sessions", ["id"])
    op.create_index("ix_planned_sessions_plan_revision_id", "planned_sessions", ["plan_revision_id"])
    op.create_index("ix_planned_sessions_user_id", "planned_sessions", ["user_id"])
    op.create_index("ix_planned_sessions_local_date", "planned_sessions", ["local_date"])
    op.create_index("ix_planned_sessions_user_date", "planned_sessions", ["user_id", "local_date"])

    # 9. activities
    op.create_table(
        "activities",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("planned_session_id", sa.String(36), sa.ForeignKey("planned_sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("local_date", sa.String(32), nullable=False),
        sa.Column("start_time_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="Asia/Kolkata"),
        sa.Column("activity_type", sa.String(64), nullable=False, server_default="running"),
        sa.Column("duration_min", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("distance_km", sa.Float(), nullable=True),
        sa.Column("perceived_effort", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("completion_state", sa.String(32), nullable=False, server_default="completed"),
        sa.Column("early_stop_reason", sa.String(64), nullable=False, server_default=""),
        sa.Column("pain_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("pain_notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("source", sa.String(64), nullable=False, server_default="manual"),
        sa.Column("confidence", sa.String(32), nullable=False, server_default="high"),
        sa.Column("is_manual", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_activities_id", "activities", ["id"])
    op.create_index("ix_activities_user_id", "activities", ["user_id"])
    op.create_index("ix_activities_planned_session_id", "activities", ["planned_session_id"])
    op.create_index("ix_activities_local_date", "activities", ["local_date"])
    op.create_index("ix_activities_user_date", "activities", ["user_id", "local_date"])

    # 10. activity_revisions
    op.create_table(
        "activity_revisions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("activity_id", sa.String(36), sa.ForeignKey("activities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("duration_min", sa.Float(), nullable=False),
        sa.Column("distance_km", sa.Float(), nullable=True),
        sa.Column("perceived_effort", sa.Integer(), nullable=False),
        sa.Column("completion_state", sa.String(32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("change_reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_activity_revisions_id", "activity_revisions", ["id"])
    op.create_index("ix_activity_revisions_activity_id", "activity_revisions", ["activity_id"])
    op.create_index("ix_activity_revisions_user_id", "activity_revisions", ["user_id"])
    op.create_index("ix_act_rev_unique", "activity_revisions", ["activity_id", "revision_number"], unique=True)

    # 11. daily_checkins
    op.create_table(
        "daily_checkins",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("local_date", sa.String(32), nullable=False),
        sa.Column("checkin_time_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sleep_duration_hours", sa.Float(), nullable=True),
        sa.Column("sleep_quality", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("energy_level", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("soreness_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("stress_level", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("pain_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("pain_area", sa.String(128), nullable=False, server_default=""),
        sa.Column("pain_severity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("red_flag_symptom", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("source", sa.String(64), nullable=False, server_default="app_home"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_daily_checkins_id", "daily_checkins", ["id"])
    op.create_index("ix_daily_checkins_user_id", "daily_checkins", ["user_id"])
    op.create_index("ix_daily_checkins_local_date", "daily_checkins", ["local_date"])
    op.create_index("ix_checkins_user_date", "daily_checkins", ["user_id", "local_date"])

    # 12. nutrition_profiles
    op.create_table(
        "nutrition_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dietary_pattern", sa.String(64), nullable=False, server_default="vegetarian"),
        sa.Column("regional_preference", sa.String(64), nullable=False, server_default="south_indian"),
        sa.Column("allergies_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("foods_avoided_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("goal_preference", sa.String(64), nullable=False, server_default="endurance_fueling"),
        sa.Column("intake_target_kcal", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_nutrition_profiles_id", "nutrition_profiles", ["id"])
    op.create_index("ix_nutrition_profiles_user_id", "nutrition_profiles", ["user_id"], unique=True)

    # 13. nutrition_guidance
    op.create_table(
        "nutrition_guidance",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("local_date", sa.String(32), nullable=False),
        sa.Column("min_kcal", sa.Integer(), nullable=False),
        sa.Column("max_kcal", sa.Integer(), nullable=False),
        sa.Column("protein_g_min", sa.Integer(), nullable=False),
        sa.Column("protein_g_max", sa.Integer(), nullable=False),
        sa.Column("carbs_g_min", sa.Integer(), nullable=False),
        sa.Column("carbs_g_max", sa.Integer(), nullable=False),
        sa.Column("fats_g_min", sa.Integer(), nullable=False),
        sa.Column("fats_g_max", sa.Integer(), nullable=False),
        sa.Column("hydration_liters", sa.Float(), nullable=False, server_default="3.0"),
        sa.Column("meal_ideas_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("rationale", sa.Text(), nullable=False, server_default=""),
        sa.Column("algorithm_version", sa.String(32), nullable=False, server_default="slickfit_nut_v1"),
        sa.Column("confidence", sa.String(32), nullable=False, server_default="medium"),
        sa.Column("limitations", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_nutrition_guidance_id", "nutrition_guidance", ["id"])
    op.create_index("ix_nutrition_guidance_user_id", "nutrition_guidance", ["user_id"])
    op.create_index("ix_nutrition_guidance_local_date", "nutrition_guidance", ["local_date"])
    op.create_index("ix_nut_guidance_user_date", "nutrition_guidance", ["user_id", "local_date"])

    # 14. data_amendments
    op.create_table(
        "data_amendments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("field_name", sa.String(64), nullable=False),
        sa.Column("prior_value", sa.Text(), nullable=False, server_default=""),
        sa.Column("replacement_value", sa.Text(), nullable=False, server_default=""),
        sa.Column("actor_user_id", sa.String(36), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("source", sa.String(64), nullable=False, server_default="user_correction"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_data_amendments_id", "data_amendments", ["id"])
    op.create_index("ix_data_amendments_user_id", "data_amendments", ["user_id"])
    op.create_index("ix_data_amendments_entity_id", "data_amendments", ["entity_id"])
    op.create_index("ix_amendments_user_entity", "data_amendments", ["user_id", "entity_type", "entity_id"])

    # 15. adaptation_events
    op.create_table(
        "adaptation_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_id", sa.String(36), sa.ForeignKey("plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("prior_plan_revision_id", sa.String(36), nullable=False),
        sa.Column("new_plan_revision_id", sa.String(36), nullable=False),
        sa.Column("trigger_inputs_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("reason_codes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("explanation", sa.Text(), nullable=False, server_default=""),
        sa.Column("algorithm_version", sa.String(32), nullable=False, server_default="slickfit_v1_rules"),
        sa.Column("user_visible_impact", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_adaptation_events_id", "adaptation_events", ["id"])
    op.create_index("ix_adaptation_events_user_id", "adaptation_events", ["user_id"])
    op.create_index("ix_adaptation_events_plan_id", "adaptation_events", ["plan_id"])
    op.create_index("ix_adaptations_user_plan", "adaptation_events", ["user_id", "plan_id"])


def downgrade() -> None:
    op.drop_table("adaptation_events")
    op.drop_table("data_amendments")
    op.drop_table("nutrition_guidance")
    op.drop_table("nutrition_profiles")
    op.drop_table("daily_checkins")
    op.drop_table("activity_revisions")
    op.drop_table("activities")
    op.drop_table("planned_sessions")
    op.drop_table("plan_revisions")
    op.drop_table("plans")
    op.drop_table("baseline_observations")
    op.drop_table("availabilities")
    op.drop_table("events")
    op.drop_table("athlete_profiles")
    op.drop_table("users")
