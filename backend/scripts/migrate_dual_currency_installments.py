"""
Migration script to add dual-currency information to existing installments.

This script finds installments that:
1. Have a purchase with exchange_rate_id set
2. But the installment itself has original_amount=None

And updates them with the correct dual-currency information.
"""
import sqlite3
from decimal import Decimal


def migrate_installments():
    """Migrate existing installments to include dual-currency data from their purchases."""
    
    # Connect to database
    conn = sqlite3.connect("/data/cashdata.db")
    cursor = conn.cursor()
    
    try:
        # Find all installments that need migration
        cursor.execute("""
            SELECT i.id, i.purchase_id, i.amount, i.currency
            FROM installments i
            WHERE i.original_amount IS NULL
        """)
        installments = cursor.fetchall()
        
        migrated_count = 0
        for installment_id, purchase_id, installment_amount, installment_currency in installments:
            # Get the purchase
            cursor.execute("""
                SELECT total_amount, total_currency, original_amount, original_currency, exchange_rate_id
                FROM purchases
                WHERE id = ?
            """, (purchase_id,))
            purchase_data = cursor.fetchone()
            
            if not purchase_data:
                print(f"WARNING: Installment {installment_id} has no purchase!")
                continue
            
            purchase_total, purchase_currency, purchase_original, purchase_orig_currency, exchange_rate_id = purchase_data
            
            # Check if purchase has dual-currency data
            if exchange_rate_id and purchase_original and purchase_orig_currency:
                # Calculate the installment's original amount
                # (proportional to the purchase's original amount)
                purchase_primary = Decimal(str(purchase_total))
                purchase_secondary = Decimal(str(purchase_original))
                installment_primary = Decimal(str(installment_amount))
                
                # Calculate proportional secondary amount
                if purchase_primary != 0:
                    ratio = installment_primary / purchase_primary
                    installment_secondary = (purchase_secondary * ratio).quantize(Decimal("0.01"))
                    
                    # Update installment
                    cursor.execute("""
                        UPDATE installments
                        SET original_amount = ?,
                            original_currency = ?,
                            exchange_rate_id = ?
                        WHERE id = ?
                    """, (float(installment_secondary), purchase_orig_currency, exchange_rate_id, installment_id))
                    
                    print(f"✓ Migrated installment {installment_id}: {installment_amount} {installment_currency} = {installment_secondary} {purchase_orig_currency}")
                    migrated_count += 1
        
        # Commit changes
        conn.commit()
        print(f"\n✅ Successfully migrated {migrated_count} installments")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("Starting dual-currency installment migration...\n")
    migrate_installments()
