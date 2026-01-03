"""Clean up duplicate monthly statements.

This script removes duplicate statements for the same credit card and billing period,
keeping only the oldest one (by ID, assuming lower ID = created first).

Run this once to fix existing duplicates after the statement_helper fix.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Use the same database URL as the application
DATABASE_URL = "sqlite:///./cashdata.db"


def clean_duplicate_statements():
    """Remove duplicate statements, keeping the oldest one per period."""

    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Find duplicates: same credit_card_id and same period (YYYYMM from billing_close_date)
        query = text(
            """
            SELECT 
                credit_card_id,
                strftime('%Y%m', billing_close_date) as period,
                GROUP_CONCAT(id ORDER BY id) as ids,
                COUNT(*) as count
            FROM monthly_statements
            GROUP BY credit_card_id, period
            HAVING COUNT(*) > 1
        """
        )

        duplicates = session.execute(query).fetchall()

        if not duplicates:
            print("✅ No duplicate statements found!")
            return

        print(f"Found {len(duplicates)} sets of duplicates:")
        print()

        total_deleted = 0

        for dup in duplicates:
            card_id, period, ids_str, count = dup
            ids = [int(id) for id in ids_str.split(",")]

            # Keep the first (oldest) ID, delete the rest
            keep_id = ids[0]
            delete_ids = ids[1:]

            print(f"Card {card_id}, Period {period}:")
            print(f"  - Keeping statement ID: {keep_id}")
            print(f"  - Deleting statement IDs: {delete_ids}")

            # Delete the duplicate statements one by one
            for delete_id in delete_ids:
                delete_query = text(
                    """
                    DELETE FROM monthly_statements
                    WHERE id = :id
                """
                )

                session.execute(delete_query, {"id": delete_id})

            deleted_count = len(delete_ids)
            total_deleted += deleted_count

            print(f"  - Deleted {deleted_count} duplicate(s)")
            print()

        session.commit()
        print(f"✅ Cleanup complete! Deleted {total_deleted} duplicate statements.")

    except Exception as e:
        session.rollback()
        print(f"❌ Error during cleanup: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("🧹 Starting cleanup of duplicate monthly statements...")
    print()
    clean_duplicate_statements()
