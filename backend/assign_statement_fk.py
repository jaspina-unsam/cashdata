"""Assign `monthly_statement_id` FK for existing purchases.

This script walks all purchases without a statement FK, determines the
statement for the purchase date (creating it if necessary) and updates the
purchase record with the statement id. Run once after deploying the schema
change.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from cashdata.infrastructure.persistence.database import DATABASE_URL, SessionLocal
from cashdata.infrastructure.persistence.repositories.sqlalchemy_unit_of_work import (
    SQLAlchemyUnitOfWork,
)

from cashdata.application.helpers.statement_helper import get_or_create_statement_for_date


def assign_statement_fk():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        query = text(
            """
            SELECT id, credit_card_id, purchase_date, monthly_statement_id
            FROM purchases
            ORDER BY id
            """
        )

        rows = session.execute(query).fetchall()

        if not rows:
            print("✅ No purchases found in database!")
            return

        # Use UnitOfWork to access repositories (statement creation, credit cards)
        uow = SQLAlchemyUnitOfWork(lambda: SessionLocal())

        updated = 0
        skipped = 0

        with uow as work:
            for row in rows:
                purchase_id, credit_card_id, purchase_date_str, current_fk = row

                if current_fk is not None:
                    skipped += 1
                    continue

                # Parse date string (YYYY-MM-DD)
                year, month, day = map(int, purchase_date_str.split("-"))
                from datetime import date

                purchase_date = date(year, month, day)

                credit_card = work.credit_cards.find_by_id(credit_card_id)
                if not credit_card:
                    print(f"⚠️  Credit card {credit_card_id} not found for purchase {purchase_id}, skipping")
                    continue

                # Get or create statement for this purchase date
                statement = get_or_create_statement_for_date(
                    credit_card=credit_card,
                    purchase_date=purchase_date,
                    statement_repository=work.monthly_statements,
                )

                # Update purchase record directly
                update_q = text(
                    """
                    UPDATE purchases
                    SET monthly_statement_id = :stmt_id
                    WHERE id = :id
                    """
                )

                session.execute(update_q, {"stmt_id": statement.id, "id": purchase_id})
                print(f"Updated purchase {purchase_id} → statement {statement.id}")
                updated += 1

            # Commit both repositories and raw session updates
            work.commit()
            session.commit()

        print()
        print("✅ Done")
        print(f"  - Updated: {updated}")
        print(f"  - Skipped (already had FK): {skipped}")

    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("Assigning monthly_statement_id to existing purchases...")
    resp = input("This will update the purchases table. Continue? (y/n): ")
    if resp.lower() == "y":
        assign_statement_fk()
    else:
        print("Cancelled")
