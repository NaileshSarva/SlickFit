"""Store the unit for a planned session's optional distance target."""

from alembic import op
import sqlalchemy as sa

revision = "002_planned_session_distance_unit"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "planned_sessions",
        sa.Column("distance_unit", sa.String(length=16), nullable=False, server_default="km"),
    )
    op.add_column(
        "nutrition_profiles",
        sa.Column("activity_level", sa.String(length=64), nullable=False, server_default="moderate"),
    )


def downgrade() -> None:
    op.drop_column("nutrition_profiles", "activity_level")
    op.drop_column("planned_sessions", "distance_unit")
