"""add_monthly_statement_fk_to_purchases

Revision ID: 3b1f7a9b8c2b
Revises: e9c143903dd1
Create Date: 2026-01-03 22:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b1f7a9b8c2b'
down_revision: Union[str, Sequence[str], None] = 'e9c143903dd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add monthly_statement_id column and foreign key to purchases."""
    op.add_column(
        'purchases',
        sa.Column('monthly_statement_id', sa.Integer(), nullable=True),
    )

    # Create a foreign key constraint to monthly_statements.id
    op.create_foreign_key(
        'fk_purchases_monthly_statement_id',
        'purchases',
        'monthly_statements',
        ['monthly_statement_id'],
        ['id'],
    )


def downgrade() -> None:
    """Remove the monthly_statement_id column and FK."""
    op.drop_constraint('fk_purchases_monthly_statement_id', 'purchases', type_='foreignkey')
    op.drop_column('purchases', 'monthly_statement_id')
