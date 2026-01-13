"""add_responsible_currency_to_expense_responsibilities

Revision ID: bfaa992b8689
Revises: 65e73ce5eadb
Create Date: 2026-01-12 18:44:26.916216

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfaa992b8689'
down_revision: Union[str, Sequence[str], None] = '65e73ce5eadb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add responsible_currency column to budget_expense_responsibilities
    op.add_column(
        'budget_expense_responsibilities',
        sa.Column('responsible_currency', sa.String(3), server_default='ARS', nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove responsible_currency column
    op.drop_column('budget_expense_responsibilities', 'responsible_currency')
