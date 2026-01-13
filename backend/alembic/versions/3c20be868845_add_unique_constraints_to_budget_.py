"""add_unique_constraints_to_budget_expenses

Revision ID: 3c20be868845
Revises: 11cb193cbf68
Create Date: 2026-01-12 19:15:45.879491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c20be868845'
down_revision: Union[str, Sequence[str], None] = '11cb193cbf68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add unique constraint for purchase_id (when not null)
    # SQLite doesn't support partial indexes via ALTER, so we create unique index with WHERE clause
    op.create_index(
        'uq_budget_expenses_purchase',
        'budget_expenses',
        ['purchase_id'],
        unique=True,
        sqlite_where=sa.text('purchase_id IS NOT NULL')
    )
    
    # Add unique constraint for installment_id (when not null)
    op.create_index(
        'uq_budget_expenses_installment',
        'budget_expenses',
        ['installment_id'],
        unique=True,
        sqlite_where=sa.text('installment_id IS NOT NULL')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop unique constraints
    op.drop_index('uq_budget_expenses_installment', table_name='budget_expenses')
    op.drop_index('uq_budget_expenses_purchase', table_name='budget_expenses')
