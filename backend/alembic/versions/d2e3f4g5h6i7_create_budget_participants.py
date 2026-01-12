"""create budget_participants table

Revision ID: d2e3f4g5h6i7
Revises: c1d2e3f4g5h6
Create Date: 2026-01-12 10:05:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression


# revision identifiers, used by Alembic.
revision: str = "d2e3f4g5h6i7"
down_revision: Union[str, Sequence[str], None] = "c1d2e3f4g5h6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "budget_participants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("budget_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), server_default="participant", nullable=False),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "role IN ('creator', 'participant')",
            name="ck_role_in_expected_list"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["budget_id"], ["monthly_budgets.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("budget_id", "user_id", name="uq_budget_participants_budget_user"),
    )
    op.create_index("idx_budget_participants_budget", "budget_participants", ["budget_id"])
    op.create_index("idx_budget_participants_user", "budget_participants", ["user_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_budget_participants_user", table_name="budget_participants")
    op.drop_index("idx_budget_participants_budget", table_name="budget_participants")
    op.drop_table("budget_participants")