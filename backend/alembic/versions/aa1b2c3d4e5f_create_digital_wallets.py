"""create digital_wallets table

Revision ID: aa1b2c3d4e5f
Revises: e76666c7a7d5
Create Date: 2026-01-12 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "aa1b2c3d4e5f"
down_revision: Union[str, Sequence[str], None] = "e76666c7a7d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "digital_wallets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("payment_method_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("identifier", sa.String(length=200), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="ARS"),
        sa.ForeignKeyConstraint(["payment_method_id"], ["payment_methods.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_digital_wallets_user_id", "digital_wallets", ["user_id"])
    op.create_index("ix_digital_wallets_payment_method_id", "digital_wallets", ["payment_method_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_digital_wallets_user_id", table_name="digital_wallets")
    op.drop_index("ix_digital_wallets_payment_method_id", table_name="digital_wallets")
    op.drop_table("digital_wallets")
