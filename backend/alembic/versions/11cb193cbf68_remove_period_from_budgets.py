"""remove_period_from_budgets

Revision ID: 11cb193cbf68
Revises: 933c620e2586
Create Date: 2026-01-12 19:15:26.385308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11cb193cbf68'
down_revision: Union[str, Sequence[str], None] = '933c620e2586'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # First drop all indexes that reference period column
    op.drop_index('idx_monthly_budgets_period_name', table_name='monthly_budgets')
    
    # Then remove period column from monthly_budgets
    op.drop_column('monthly_budgets', 'period')


def downgrade() -> None:
    """Downgrade schema."""
    # Add period column back to monthly_budgets
    op.add_column('monthly_budgets', 
                  sa.Column('period', sa.String(6), nullable=True))
    
    # Recreate the index
    op.create_index('idx_monthly_budgets_period_name', 'monthly_budgets', ['period', 'name'])
