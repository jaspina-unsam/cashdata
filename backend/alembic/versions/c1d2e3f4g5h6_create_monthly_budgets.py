"""create monthly_budgets table

Revision ID: c1d2e3f4g5h6
Revises: f806e597ef9a
Create Date: 2026-01-12 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression


# revision identifiers, used by Alembic.
revision: str = "c1d2e3f4g5h6"
down_revision: Union[str, Sequence[str], None] = "f806e597ef9a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "monthly_budgets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("period", sa.String(length=6), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
        ),
        sa.CheckConstraint(
            "status IN ('active', 'closed', 'archived')",
            name="ck_status_in_expected_list"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
    )
    op.create_index("idx_monthly_budgets_period", "monthly_budgets", ["period"])
    op.create_index("idx_monthly_budgets_created_by", "monthly_budgets", ["created_by_user_id"])
    op.create_index("idx_monthly_budgets_period_name", "monthly_budgets", ["period", "name"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_monthly_budgets_period_name", table_name="monthly_budgets")
    op.drop_index("idx_monthly_budgets_created_by", table_name="monthly_budgets")
    op.drop_index("idx_monthly_budgets_period", table_name="monthly_budgets")
    op.drop_table("monthly_budgets")