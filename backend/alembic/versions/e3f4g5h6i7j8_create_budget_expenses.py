"""create budget_expenses table

Revision ID: e3f4g5h6i7j8
Revises: d2e3f4g5h6i7
Create Date: 2026-01-12 10:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression


# revision identifiers, used by Alembic.
revision: str = "e3f4g5h6i7j8"
down_revision: Union[str, Sequence[str], None] = "d2e3f4g5h6i7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "budget_expenses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("budget_id", sa.Integer(), nullable=False),
        sa.Column("purchase_id", sa.Integer(), nullable=True),
        sa.Column("installment_id", sa.Integer(), nullable=True),
        sa.Column("paid_by_user_id", sa.Integer(), nullable=False),
        sa.Column("split_type", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), server_default="ARS", nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("payment_method_name", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "split_type IN ('equal', 'proportional', 'custom', 'full_single')",
            name="ck_split_type_in_expected_list"
        ),
        sa.CheckConstraint(
            "NOT (purchase_id IS NOT NULL AND installment_id IS NOT NULL)",
            name="ck_xor_purchase_installment"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["budget_id"], ["monthly_budgets.id"]),
        sa.ForeignKeyConstraint(["purchase_id"], ["purchases.id"]),
        sa.ForeignKeyConstraint(["installment_id"], ["installments.id"]),
        sa.ForeignKeyConstraint(["paid_by_user_id"], ["users.id"]),
    )
    op.create_index("idx_budget_expenses_budget", "budget_expenses", ["budget_id"])
    op.create_index("idx_budget_expenses_purchase", "budget_expenses", ["purchase_id"])
    op.create_index("idx_budget_expenses_installment", "budget_expenses", ["installment_id"])
    op.create_index("idx_budget_expenses_paid_by", "budget_expenses", ["paid_by_user_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_budget_expenses_paid_by", table_name="budget_expenses")
    op.drop_index("idx_budget_expenses_installment", table_name="budget_expenses")
    op.drop_index("idx_budget_expenses_purchase", table_name="budget_expenses")
    op.drop_index("idx_budget_expenses_budget", table_name="budget_expenses")
    op.drop_table("budget_expenses")