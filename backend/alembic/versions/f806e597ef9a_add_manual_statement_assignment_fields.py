"""add manual statement assignment fields

Revision ID: f806e597ef9a
Revises: 3f64d359117e
Create Date: 2026-01-07 22:24:14.145890

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f806e597ef9a"
down_revision: Union[str, Sequence[str], None] = "3f64d359117e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ONLY add to installments table:
    with op.batch_alter_table("installments") as batch_op:
        batch_op.add_column(
            sa.Column("manually_assigned_statement_id", sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            "fk_installment_manual_statement",
            "monthly_statements",
            ["manually_assigned_statement_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index(
            "ix_installments_manual_statement",
            ["manually_assigned_statement_id"],
        )

    # DO NOT add to purchases table


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("installments") as batch_op:
        batch_op.drop_index("ix_installments_manual_statement")
        batch_op.drop_constraint(
            "fk_installment_manual_statement", type_="foreignkey"
        )
        batch_op.drop_column("manually_assigned_statement_id")
