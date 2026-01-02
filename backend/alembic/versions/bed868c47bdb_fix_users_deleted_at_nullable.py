"""fix_users_deleted_at_nullable

Revision ID: bed868c47bdb
Revises: 86be928e503b
Create Date: 2026-01-02 16:15:36.736982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bed868c47bdb'
down_revision: Union[str, Sequence[str], None] = '86be928e503b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make deleted_at nullable for soft delete pattern
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('deleted_at',
                              existing_type=sa.DateTime(timezone=True),
                              nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Revert deleted_at to NOT NULL
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('deleted_at',
                              existing_type=sa.DateTime(timezone=True),
                              nullable=False)
