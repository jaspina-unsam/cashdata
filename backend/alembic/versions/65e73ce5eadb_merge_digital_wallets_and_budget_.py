"""merge digital wallets and budget branches

Revision ID: 65e73ce5eadb
Revises: aa1b2c3d4e5f, f4g5h6i7j8k9
Create Date: 2026-01-12 16:56:43.414329

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65e73ce5eadb'
down_revision: Union[str, Sequence[str], None] = ('aa1b2c3d4e5f', 'f4g5h6i7j8k9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
