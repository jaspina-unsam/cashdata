"""create_monthly_statements_table

Revision ID: e9c143903dd1
Revises: bed868c47bdb
Create Date: 2026-01-02 17:14:53.534998

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9c143903dd1'
down_revision: Union[str, Sequence[str], None] = 'bed868c47bdb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'monthly_statements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('credit_card_id', sa.Integer(), nullable=False),
        sa.Column('closing_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['credit_card_id'], ['credit_cards.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Create index for efficient queries by credit card
    op.create_index('ix_monthly_statements_credit_card_id', 'monthly_statements', ['credit_card_id'])
    # Create index for efficient queries by due date
    op.create_index('ix_monthly_statements_due_date', 'monthly_statements', ['due_date'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_monthly_statements_due_date', table_name='monthly_statements')
    op.drop_index('ix_monthly_statements_credit_card_id', table_name='monthly_statements')
    op.drop_table('monthly_statements')
