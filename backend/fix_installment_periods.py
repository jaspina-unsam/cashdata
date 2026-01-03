"""Fix all installment billing periods based on their due dates.

This script recalculates the billing_period for all installments in the database
using the new logic: billing_period = month(due_date) - 1

Run this once after the refactor to fix existing data.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import date

# Use the same database URL as the application
DATABASE_URL = "sqlite:///./cashdata.db"


def fix_installment_periods():
    """Recalculate billing_period for all installments based on due_date."""

    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get all installments with their current due_date and billing_period
        query = text(
            """
            SELECT id, due_date, billing_period
            FROM installments
            ORDER BY id
            """
        )

        installments = session.execute(query).fetchall()

        if not installments:
            print("✅ No installments found in database!")
            return

        print(f"Found {len(installments)} installments to process")
        print()

        updated_count = 0
        unchanged_count = 0

        for inst in installments:
            inst_id, due_date_str, current_period = inst

            # Parse due_date (format: YYYY-MM-DD)
            year, month, day = map(int, due_date_str.split('-'))
            
            # Calculate correct billing_period (due_month - 1)
            period_month = month - 1
            period_year = year
            if period_month < 1:
                period_month = 12
                period_year -= 1
            
            correct_period = f"{period_year:04d}{period_month:02d}"

            # Update if different
            if current_period != correct_period:
                update_query = text(
                    """
                    UPDATE installments
                    SET billing_period = :new_period
                    WHERE id = :id
                    """
                )

                session.execute(
                    update_query,
                    {"id": inst_id, "new_period": correct_period}
                )

                print(f"Installment {inst_id}: {current_period} → {correct_period} (due: {due_date_str})")
                updated_count += 1
            else:
                unchanged_count += 1

        session.commit()
        
        print()
        print(f"✅ Fix complete!")
        print(f"   - Updated: {updated_count} installments")
        print(f"   - Already correct: {unchanged_count} installments")

    except Exception as e:
        session.rollback()
        print(f"❌ Error during fix: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("🔧 Fixing installment billing periods...")
    print("Using new logic: billing_period = month(due_date) - 1")
    print()
    
    response = input("This will update all installments in the database. Continue? (y/n): ")
    if response.lower() == 'y':
        fix_installment_periods()
    else:
        print("❌ Cancelled by user")
