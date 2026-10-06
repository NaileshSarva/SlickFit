"""Integration test verifying Alembic schema migrations."""

import os
import tempfile
from pathlib import Path

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_and_downgrade():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = Path(tmpdir) / "migration_test.db"
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{test_db_path}")

        # Run upgrade to head
        command.upgrade(alembic_cfg, "head")

        engine = create_engine(f"sqlite:///{test_db_path}")
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())

        expected_tables = {
            "users",
            "athlete_profiles",
            "events",
            "availabilities",
            "baseline_observations",
            "plans",
            "plan_revisions",
            "planned_sessions",
            "activities",
            "activity_revisions",
            "daily_checkins",
            "nutrition_profiles",
            "nutrition_guidance",
            "data_amendments",
            "adaptation_events",
            "alembic_version",
        }

        assert expected_tables.issubset(tables)

        # Run downgrade to base
        command.downgrade(alembic_cfg, "base")
        inspector = inspect(engine)
        remaining_tables = set(inspector.get_table_names())
        assert remaining_tables == {"alembic_version"} or remaining_tables == set()

        # Re-upgrade to head
        command.upgrade(alembic_cfg, "head")
        inspector = inspect(engine)
        assert expected_tables.issubset(set(inspector.get_table_names()))
