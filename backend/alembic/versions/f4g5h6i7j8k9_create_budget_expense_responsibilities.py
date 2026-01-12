"""create budget_expense_responsibilities table

Revision ID: f4g5h6i7j8k9
Revises: e3f4g5h6i7j8
Create Date: 2026-01-12 10:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression


# revision identifiers, used by Alembic.
revision: str = "f4g5h6i7j8k9"
down_revision: Union[str, Sequence[str], None] = "e3f4g5h6i7j8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "budget_expense_responsibilities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("budget_expense_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("percentage", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("responsible_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.CheckConstraint(
            "percentage >= 0 AND percentage <= 100",
            name="ck_percentage_range"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["budget_expense_id"], ["budget_expenses.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("budget_expense_id", "user_id", name="uq_expense_responsibilities_expense_user"),
    )
    op.create_index("idx_expense_responsibilities_expense", "budget_expense_responsibilities", ["budget_expense_id"])
    op.create_index("idx_expense_responsibilities_user", "budget_expense_responsibilities", ["user_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_expense_responsibilities_user", table_name="budget_expense_responsibilities")
    op.drop_index("idx_expense_responsibilities_expense", table_name="budget_expense_responsibilities")
    op.drop_table("budget_expense_responsibilities")