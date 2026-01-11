"""rename credit_card_id to payment_method_id in purchases

Revision ID: 0c67ef27dd8f
Revises: e92f1dfc8478
Create Date: 2026-01-10 10:29:24.852901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c67ef27dd8f'
down_revision: Union[str, Sequence[str], None] = 'e92f1dfc8478'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new column
    op.add_column("purchases", sa.Column("payment_method_id", sa.Integer, nullable=True))

    # Populate with payment_method_id from credit_cards
    op.execute(
        "UPDATE purchases SET payment_method_id = (SELECT credit_cards.payment_method_id FROM credit_cards WHERE credit_cards.id = purchases.credit_card_id)"
    )

    # Drop old FK, drop old column, add new FK, set nullable=False
    with op.batch_alter_table("purchases") as batch_op:
        batch_op.drop_column("credit_card_id")
        batch_op.create_foreign_key(
            "fk_purchases_payment_method_id",
            "payment_methods",
            ["payment_method_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.alter_column("payment_method_id", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Add back credit_card_id
    op.add_column("purchases", sa.Column("credit_card_id", sa.Integer, nullable=True))

    # Populate with credit_card id that has the payment_method_id
    op.execute(
        "UPDATE purchases SET credit_card_id = (SELECT credit_cards.id FROM credit_cards WHERE credit_cards.payment_method_id = purchases.payment_method_id)"
    )

    # Drop FK, drop column, add old FK, set nullable=False
    with op.batch_alter_table("purchases") as batch_op:
        batch_op.drop_column("payment_method_id")
        batch_op.create_foreign_key(
            "fk_purchases_credit_card_id",
            "credit_cards",
            ["credit_card_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.alter_column("credit_card_id", nullable=False)
