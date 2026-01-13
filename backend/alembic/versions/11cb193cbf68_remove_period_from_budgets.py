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
    # Check if period column exists before attempting to drop it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('monthly_budgets')]
    
    if 'period' not in columns:
        # Column already removed or never existed, nothing to do
        return
    
    # First drop ALL indexes that reference period column
    for index_name in ['idx_monthly_budgets_period', 'idx_monthly_budgets_period_name']:
        try:
            op.drop_index(index_name, table_name='monthly_budgets')
        except Exception:
            pass  # Index might not exist
    
    # Then remove period column from monthly_budgets
    op.drop_column('monthly_budgets', 'period')


def downgrade() -> None:
    """Downgrade schema."""
    # Add period column back to monthly_budgets
    op.add_column('monthly_budgets', 
                  sa.Column('period', sa.String(6), nullable=True))
    
    # Recreate the index
    op.create_index('idx_monthly_budgets_period_name', 'monthly_budgets', ['period', 'name'])
