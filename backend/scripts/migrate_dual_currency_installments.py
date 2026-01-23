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
        # (either original_amount is NULL OR exchange_rate_id is NULL)
        cursor.execute("""
            SELECT i.id, i.purchase_id, i.amount, i.currency, i.original_amount, i.exchange_rate_id
            FROM installments i
            WHERE i.original_amount IS NULL OR i.exchange_rate_id IS NULL
        """)
        installments = cursor.fetchall()
        
        migrated_count = 0
        skipped_count = 0
        
        for installment_id, purchase_id, installment_amount, installment_currency, current_original_amount, current_exchange_rate_id in installments:
            # Get the purchase
            cursor.execute("""
                SELECT total_amount, total_currency, original_amount, original_currency, exchange_rate_id
                FROM purchases
                WHERE id = ?
            """, (purchase_id,))
            purchase_data = cursor.fetchone()
            
            if not purchase_data:
                print(f"WARNING: Installment {installment_id} has no purchase!")
                skipped_count += 1
                continue
            
            purchase_total, purchase_currency, purchase_original, purchase_orig_currency, exchange_rate_id = purchase_data
            
            # Skip if purchase doesn't have dual-currency data
            if not exchange_rate_id or not purchase_original or not purchase_orig_currency:
                print(f"  Skipping installment {installment_id} (purchase {purchase_id} has no dual-currency data)")
                skipped_count += 1
                continue
                skipped_count += 1
                continue
                
            # Calculate or reuse the installment's original amount
            if current_original_amount:
                # Already has original_amount, just need to add exchange_rate_id
                installment_secondary = Decimal(str(current_original_amount))
            else:
                # Calculate the installment's original amount
                # (proportional to the purchase's original amount)
                purchase_primary = Decimal(str(purchase_total))
                purchase_secondary = Decimal(str(purchase_original))
                installment_primary = Decimal(str(installment_amount))
                
                # Calculate proportional secondary amount
                if purchase_primary != 0:
                    ratio = installment_primary / purchase_primary
                    installment_secondary = (purchase_secondary * ratio).quantize(Decimal("0.01"))
                else:
                    print(f"WARNING: Purchase {purchase_id} has zero amount, skipping installment {installment_id}")
                    skipped_count += 1
                    continue
            
            # Update installment (set both fields, even if one already exists)
            cursor.execute("""
                UPDATE installments
                SET original_amount = ?,
                    original_currency = ?,
                    exchange_rate_id = ?
                WHERE id = ?
            """, (float(installment_secondary), purchase_orig_currency, exchange_rate_id, installment_id))
            
            status = "Updated" if current_original_amount else "Migrated"
            print(f"✓ {status} installment {installment_id}: {installment_amount} {installment_currency} = {installment_secondary} {purchase_orig_currency} (exchange_rate_id={exchange_rate_id})")
            migrated_count += 1
        
        # Commit changes
        conn.commit()
        print(f"\n✅ Successfully migrated {migrated_count} installments ({skipped_count} skipped)")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("Starting dual-currency installment migration...\n")
    migrate_installments()
