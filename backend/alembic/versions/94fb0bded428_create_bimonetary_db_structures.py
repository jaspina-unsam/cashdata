"""create bimonetary db structures

Revision ID: 94fb0bded428
Revises: 3c20be868845
Create Date: 2026-01-22 13:00:03.658265

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "94fb0bded428"
down_revision: Union[str, Sequence[str], None] = "3c20be868845"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "exchange_rates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column(
            "from_currency", sa.String(length=3), nullable=False, server_default="USD"
        ),
        sa.Column(
            "to_currency", sa.String(length=3), nullable=False, server_default="ARS"
        ),
        sa.Column("rate", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column("rate_type", sa.String(length=20), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "date",
            "from_currency",
            "to_currency",
            "rate_type",
            name="uq_exchange_rates_date_from_to_rate_type",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.CheckConstraint("rate > 0", name="ck_exchange_rates_rate_positive"),
        sa.CheckConstraint(
            "rate_type IN ('official', 'blue', 'mep', 'ccl', 'custom', 'inferred')",
            name="ck_exchange_rates_rate_type_in_expected_list",
        ),
    )
    op.create_index("ix_exchange_rates_date", "exchange_rates", ["date"])
    op.create_index(
        "ix_exchange_rates_currencies",
        "exchange_rates",
        ["from_currency", "to_currency"],
    )
    op.create_index("ix_exchange_rates_type", "exchange_rates", ["rate_type"])
    op.create_index(
        "ix_exchange_rates_date_type", "exchange_rates", ["date", "rate_type"]
    )

    ## the next part of the migration is to update purchases table: add columns original_currency, original_amount and exchange_rate_id (FK from exchange_rates)
    with op.batch_alter_table("purchases") as batch_op:
        batch_op.add_column(
            sa.Column("original_currency", sa.String(length=3), nullable=True),
        )
        batch_op.add_column(
            sa.Column("original_amount", sa.Numeric(precision=12, scale=2), nullable=True),
        )
        batch_op.add_column(
            sa.Column("exchange_rate_id", sa.Integer(), nullable=True),
        )
        batch_op.create_foreign_key(
            "fk_purchases_exchange_rate_id",
            "exchange_rates",
            ["exchange_rate_id"],
            ["id"],
        )

    ## same as above, but for installments table
    with op.batch_alter_table("installments") as batch_op:
        batch_op.add_column(
            sa.Column("original_currency", sa.String(length=3), nullable=True),
        )
        batch_op.add_column(
            sa.Column("original_amount", sa.Numeric(precision=12, scale=2), nullable=True),
        )
        batch_op.add_column(
            sa.Column("exchange_rate_id", sa.Integer(), nullable=True),
        )
        batch_op.create_foreign_key(
            "fk_installments_exchange_rate_id",
            "exchange_rates",
            ["exchange_rate_id"],
            ["id"],
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("purchases") as batch_op:
        batch_op.drop_constraint("fk_purchases_exchange_rate_id", type_="foreignkey")
        batch_op.drop_column("exchange_rate_id")
        batch_op.drop_column("original_amount")
        batch_op.drop_column("original_currency")

    with op.batch_alter_table("installments") as batch_op:
        batch_op.drop_constraint("fk_installments_exchange_rate_id", type_="foreignkey")
        batch_op.drop_column("exchange_rate_id")
        batch_op.drop_column("original_amount")
        batch_op.drop_column("original_currency")

    op.drop_index("ix_exchange_rates_date_type", table_name="exchange_rates")
    op.drop_index("ix_exchange_rates_type", table_name="exchange_rates")
    op.drop_index("ix_exchange_rates_currencies", table_name="exchange_rates")
    op.drop_index("ix_exchange_rates_date", table_name="exchange_rates")
    op.drop_table("exchange_rates")
