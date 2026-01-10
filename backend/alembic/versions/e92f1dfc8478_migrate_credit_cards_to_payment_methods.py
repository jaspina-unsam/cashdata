"""migrate credit cards to payment methods

Revision ID: e92f1dfc8478
Revises: 7c83923e9ba7
Create Date: 2026-01-10 10:00:45.846477

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e92f1dfc8478"
down_revision: Union[str, Sequence[str], None] = "7c83923e9ba7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add the column as nullable
    op.add_column("credit_cards", sa.Column("payment_method_id", sa.Integer(), nullable=True))

    bind = op.get_bind()

    # Get all credit cards
    credit_cards = bind.execute(
        sa.text("SELECT id, user_id, name FROM credit_cards")
    ).fetchall()

    for cc in credit_cards:
        # Insert into payment_methods
        result = bind.execute(
            sa.text(
                "INSERT INTO payment_methods (user_id, type, name, is_active) VALUES (:user_id, :type, :name, :is_active) RETURNING id"
            ),
            {
                "user_id": cc.user_id,
                "type": "credit_card",
                "name": cc.name,
                "is_active": True,
            },
        )
        new_id = result.fetchone()[0]

        # Update credit_cards
        bind.execute(
            sa.text(
                "UPDATE credit_cards SET payment_method_id = :pm_id WHERE id = :cc_id"
            ),
            {"pm_id": new_id, "cc_id": cc.id},
        )

    # Now, add FK and set NOT NULL
    with op.batch_alter_table("credit_cards") as batch_op:
        batch_op.create_foreign_key(
            "fk_credit_cards_payment_method_id",
            "payment_methods",
            ["payment_method_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch_op.alter_column("payment_method_id", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # First, make the column nullable to allow setting to NULL
    with op.batch_alter_table("credit_cards") as batch_op:
        batch_op.alter_column("payment_method_id", nullable=True)

    # Remove the data
    op.execute(
        "UPDATE credit_cards SET payment_method_id = NULL WHERE payment_method_id IS NOT NULL"
    )
    op.execute("DELETE FROM payment_methods WHERE type = 'credit_card'")

    # Drop FK and column
    with op.batch_alter_table("credit_cards") as batch_op:
        batch_op.drop_constraint(
            "fk_credit_cards_payment_method_id", type_="foreignkey"
        )
        batch_op.drop_column("payment_method_id")
