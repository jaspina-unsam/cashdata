"""remove_period_from_budgets

Revision ID: 933c620e2586
Revises: bfaa992b8689
Create Date: 2026-01-12 19:15:20.334771

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '933c620e2586'
down_revision: Union[str, Sequence[str], None] = 'bfaa992b8689'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
