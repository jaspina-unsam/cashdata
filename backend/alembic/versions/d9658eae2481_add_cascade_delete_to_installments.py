"""add cascade delete to installments

Revision ID: d9658eae2481
Revises: f806e597ef9a
Create Date: 2026-01-08 10:29:52.278380

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d9658eae2481"
down_revision: Union[str, Sequence[str], None] = "f806e597ef9a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add CASCADE delete to installments.purchase_id FK."""
    # SQLite doesn't support modifying foreign keys, so we need to recreate the table

    # Step 1: Create new table with CASCADE
    op.execute(
        """
        CREATE TABLE installments_new (
            id INTEGER NOT NULL,
            purchase_id INTEGER NOT NULL,
            installment_number INTEGER NOT NULL,
            total_installments INTEGER NOT NULL,
            amount NUMERIC(12, 2) NOT NULL,
            currency VARCHAR(3) NOT NULL,
            billing_period VARCHAR(6) NOT NULL,
            manually_assigned_statement_id INTEGER,
            PRIMARY KEY (id),
            CONSTRAINT fk_installment_manual_statement 
                FOREIGN KEY(manually_assigned_statement_id) 
                REFERENCES monthly_statements (id) 
                ON DELETE SET NULL,
            CONSTRAINT fk_installment_purchase 
                FOREIGN KEY(purchase_id) 
                REFERENCES purchases (id) 
                ON DELETE CASCADE
        )
    """
    )

    # Step 2: Copy all data from old table to new table
    op.execute(
        """
        INSERT INTO installments_new 
        SELECT id, purchase_id, installment_number, total_installments, 
               amount, currency, billing_period, manually_assigned_statement_id
        FROM installments
    """
    )

    # Step 3: Drop the old table
    op.execute("DROP TABLE installments")

    # Step 4: Rename new table to original name
    op.execute("ALTER TABLE installments_new RENAME TO installments")

    # Step 5: Recreate the index
    op.create_index(
        "ix_installments_manual_statement",
        "installments",
        ["manually_assigned_statement_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema - Remove CASCADE delete from installments.purchase_id FK."""
    # Create table without CASCADE
    op.execute(
        """
        CREATE TABLE installments_new (
            id INTEGER NOT NULL,
            purchase_id INTEGER NOT NULL,
            installment_number INTEGER NOT NULL,
            total_installments INTEGER NOT NULL,
            amount NUMERIC(12, 2) NOT NULL,
            currency VARCHAR(3) NOT NULL,
            billing_period VARCHAR(6) NOT NULL,
            manually_assigned_statement_id INTEGER,
            PRIMARY KEY (id),
            CONSTRAINT fk_installment_manual_statement 
                FOREIGN KEY(manually_assigned_statement_id) 
                REFERENCES monthly_statements (id) 
                ON DELETE SET NULL,
            FOREIGN KEY(purchase_id) 
                REFERENCES purchases (id)
        )
    """
    )

    # Copy data back
    op.execute(
        """
        INSERT INTO installments_new 
        SELECT id, purchase_id, installment_number, total_installments, 
               amount, currency, billing_period, manually_assigned_statement_id
        FROM installments
    """
    )

    # Drop and rename
    op.execute("DROP TABLE installments")
    op.execute("ALTER TABLE installments_new RENAME TO installments")

    # Recreate index
    op.create_index(
        "ix_installments_manual_statement",
        "installments",
        ["manually_assigned_statement_id"],
        unique=False,
    )
