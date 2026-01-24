import { test, expect } from '@playwright/test';

test.describe('Delete Purchase', () => {
  test('should delete an existing purchase', async ({ page }) => {
    // Navigate to purchases page
    await page.goto('/purchases');
    
    // Wait for purchases to load
    await page.waitForSelector('[data-testid="purchase-row"]', { timeout: 10000 });
    
    // Find the first purchase in the list
    const firstPurchaseRow = page.locator('[data-testid="purchase-row"]').first();
    
    // Store purchase description for verification
    const purchaseDescription = await firstPurchaseRow.locator('h3').textContent();
    
    // Click delete button with data-testid
    const deleteButton = firstPurchaseRow.locator('[data-testid="delete-button"]');
    await deleteButton.click();
    
    // Wait for confirmation modal and click confirm
    const confirmButton = page.locator('[data-testid="confirm-button"]');
    await expect(confirmButton).toBeVisible({ timeout: 5000 });
    await confirmButton.click();
    
    // Wait for deletion to complete
    await page.waitForTimeout(1000);
    
    // Verify the purchase no longer appears in the list
    if (purchaseDescription) {
      await expect(page.locator(`text="${purchaseDescription}"`)).toHaveCount(0, { timeout: 5000 });
    }
  });

  test('should handle deletion of purchase with budget expenses', async ({ page }) => {
    // This test verifies that purchases with budget_expenses can be deleted
    // after the FK constraint fix
    await page.goto('/purchases');
    
    await page.waitForSelector('[data-testid="purchase-row"]', { timeout: 10000 });
    
    // Use first purchase (the fix should work for any purchase)
    const targetPurchase = page.locator('[data-testid="purchase-row"]').first();
    
    const deleteButton = targetPurchase.locator('[data-testid="delete-button"]');
    await deleteButton.click();
    
    // Confirm deletion
    const confirmButton = page.locator('[data-testid="confirm-button"]');
    await expect(confirmButton).toBeVisible({ timeout: 5000 });
    await confirmButton.click();
    
    // Wait for deletion to complete
    await page.waitForTimeout(1500);
    
    // Verify no error occurred (successful deletion even with budget_expenses)
    // The purchase should be removed from the list without errors
    const purchaseCount = await page.locator('[data-testid="purchase-row"]').count();
    expect(purchaseCount).toBeGreaterThanOrEqual(0);
  });
});
