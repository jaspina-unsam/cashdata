"""add_start_date_to_monthly_statements

Revision ID: 397ae91a41e4
Revises: 3b1f7a9b8c2b
Create Date: 2026-01-06 13:26:04.975447

"""

from datetime import timedelta, date
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = "397ae91a41e4"
down_revision: Union[str, Sequence[str], None] = "3b1f7a9b8c2b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add start_date column with backfill logic."""

    # Columns already renamed in previous run

    # Step 1: Add column as nullable
    op.add_column(
        "monthly_statements", sa.Column("start_date", sa.Date(), nullable=True)
    )

    # Step 2: Backfill start_date
    # Logic: start_date = previous statement's closing_date + 1 day
    #        If no previous, use closing_date - 30 days (estimate)

    connection = op.get_bind()

    # Get all statements ordered by card and closing date
    result = connection.execute(
        text(
            """
        SELECT id, credit_card_id, closing_date
        FROM monthly_statements
        ORDER BY credit_card_id, closing_date
    """
        )
    )

    statements = result.fetchall()

    # Group by card
    by_card = {}
    for stmt_id, card_id, closing_date in statements:
        if card_id not in by_card:
            by_card[card_id] = []
        by_card[card_id].append((stmt_id, closing_date))

    # Calculate start dates
    for card_id, stmts in by_card.items():
        for i, (stmt_id, closing_date) in enumerate(stmts):
            if i == 0:
                # First statement - estimate 30 days before close
                start_date = date.fromisoformat(closing_date) - timedelta(days=30)
            else:
                # Subsequent - day after previous closing
                prev_closing = date.fromisoformat(stmts[i - 1][1])
                start_date = prev_closing + timedelta(days=1)

            # Update statement
            connection.execute(
                text(
                    """
                UPDATE monthly_statements
                SET start_date = :start_date
                WHERE id = :stmt_id
            """
                ),
                {"start_date": start_date, "stmt_id": stmt_id},
            )

    # Step 3: Make column NOT NULL and add constraint
    with op.batch_alter_table("monthly_statements") as batch_op:
        batch_op.alter_column("start_date", nullable=False)
        batch_op.create_check_constraint(
            "ck_monthly_statements_dates_order",
            "start_date < closing_date AND closing_date <= due_date",
        )


def downgrade() -> None:
    """Remove start_date column."""
    with op.batch_alter_table("monthly_statements") as batch_op:
        batch_op.drop_constraint("ck_monthly_statements_dates_order")
        batch_op.drop_column("start_date")

    # Columns renamed back in separate migration if needed
