"""create payment methods table

Revision ID: 7c83923e9ba7
Revises: d9658eae2481
Create Date: 2026-01-09 21:41:11.446262

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression


# revision identifiers, used by Alembic.
revision: str = "7c83923e9ba7"
down_revision: Union[str, Sequence[str], None] = "d9658eae2481"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "payment_methods",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=expression.true(), nullable=False),
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
            "type IN ('credit_card', 'cash', 'bank_account', 'digital_wallet')",
            name="ck_type_in_expected_list"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_payment_methods_user_id", "payment_methods", ["user_id"])
    op.create_index("ix_payment_methods_type", "payment_methods", ["type"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_payment_methods_user_id", table_name="payment_methods")
    op.drop_index("ix_payment_methods_type", table_name="payment_methods")
    op.drop_table("payment_methods")
