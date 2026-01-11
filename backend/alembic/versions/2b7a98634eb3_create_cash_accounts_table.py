"""create cash_accounts table

Revision ID: 2b7a98634eb3
Revises: 0c67ef27dd8f
Create Date: 2026-01-11 09:22:11.689730

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2b7a98634eb3"
down_revision: Union[str, Sequence[str], None] = "0c67ef27dd8f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "cash_accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("payment_method_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "currency", sa.String(length=3), nullable=False, server_default="ARS"
        ),
        sa.ForeignKeyConstraint(["payment_method_id"], ["payment_methods.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cash_accounts_user_id", "cash_accounts", ["user_id"])
    op.create_index(
        "ix_cash_accounts_payment_method_id", "cash_accounts", ["payment_method_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_cash_accounts_user_id", table_name="cash_accounts")
    op.drop_index("ix_cash_accounts_payment_method_id", table_name="cash_accounts")
    op.drop_table("cash_accounts")
