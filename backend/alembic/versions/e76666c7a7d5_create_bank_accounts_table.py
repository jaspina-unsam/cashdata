"""create bank_accounts table

Revision ID: e76666c7a7d5
Revises: 2b7a98634eb3
Create Date: 2026-01-11 14:05:32.194708

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e76666c7a7d5"
down_revision: Union[str, Sequence[str], None] = "2b7a98634eb3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "bank_accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("payment_method_id", sa.Integer(), nullable=False),
        sa.Column("primary_user_id", sa.Integer(), nullable=False),
        sa.Column("secondary_user_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("bank", sa.String(length=100), nullable=False),
        sa.Column(
            "account_type",
            sa.String(length=50),
            nullable=False,
            server_default="SAVINGS",
        ),
        sa.Column("last_four_digits", sa.String(length=4), nullable=False),
        sa.Column(
            "currency", sa.String(length=3), nullable=False, server_default="ARS"
        ),
        sa.ForeignKeyConstraint(
            ["payment_method_id"], ["payment_methods.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["primary_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["secondary_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "primary_user_id != secondary_user_id",
            name="ck_bank_accounts_different_users",
        ),
    )
    # Indexes for both user IDs
    op.create_index(
        "ix_bank_accounts_primary_user_id", "bank_accounts", ["primary_user_id"]
    )
    op.create_index(
        "ix_bank_accounts_secondary_user_id", "bank_accounts", ["secondary_user_id"]
    )
    op.create_index(
        "ix_bank_accounts_payment_method_id", "bank_accounts", ["payment_method_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_bank_accounts_primary_user_id", table_name="bank_accounts")
    op.drop_index("ix_bank_accounts_secondary_user_id", table_name="bank_accounts")
    op.drop_index("ix_bank_accounts_payment_method_id", table_name="bank_accounts")
    op.drop_table("bank_accounts")
