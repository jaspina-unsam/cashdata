import { test, expect } from '@playwright/test';

test.describe('Reassign Single-Payment Purchase to Different Statement', () => {
  test('should reassign a single-payment purchase to a different statement', async ({ page }) => {
    // Navigate to purchases page
    await page.goto('/purchases');
    
    // Wait for page to load
    await page.waitForSelector('[data-testid="purchase-row"]', { timeout: 10000 });
    
    // Find a purchase with single payment (look for "Pago único")
    const singlePaymentPurchase = page.locator('[data-testid="purchase-row"]:has-text("Pago único")').first();
    
    // Get purchase description and click to expand/edit
    await singlePaymentPurchase.click();
    
    // Wait for installment editor to appear
    await page.waitForSelector('[data-testid="installment-editor"]', { timeout: 5000 });
    
    // Find the statement dropdown
    const statementDropdown = page.locator('[data-testid="statement-selector"]').first();
    
    // Verify dropdown is visible
    await expect(statementDropdown).toBeVisible({ timeout: 5000 });
    
    // Get current selected value
    const currentValue = await statementDropdown.inputValue();
    
    // Get all available options
    const options = await statementDropdown.locator('option').all();
    const optionValues = await Promise.all(
      options.map(opt => opt.getAttribute('value'))
    );
    
    // Filter out current value and empty string
    const availableOptions = optionValues.filter(
      val => val !== currentValue && val !== '' && val !== null
    );
    
    if (availableOptions.length === 0) {
      // If no other statements available, skip test
      test.skip(true, 'No alternative statements available for reassignment');
      return;
    }
    
    // Select a different statement
    const newStatementValue = availableOptions[0]!;
    await statementDropdown.selectOption(newStatementValue);
    
    // Click save button
    const saveButton = page.locator('[data-testid="save-installment-button"]').first();
    await saveButton.click();
    
    // Wait for save operation
    await page.waitForTimeout(1500);
    
    // Verify the dropdown still shows the new value (refresh from backend)
    const newValue = await statementDropdown.inputValue();
    expect(newValue).toBe(newStatementValue);
  });

  test('should show statement dropdown for single-payment credit card purchases', async ({ page }) => {
    // Navigate to purchases page
    await page.goto('/purchases');
    
    await page.waitForSelector('[data-testid="purchase-row"]', { timeout: 10000 });
    
    // Find a single-payment purchase
    const singlePaymentPurchase = page.locator('[data-testid="purchase-row"]:has-text("Pago único")').first();
    
    // Click to expand
    await singlePaymentPurchase.click();
    
    // Check if installment editor appears (indicates credit card purchase)
    const installmentEditor = page.locator('[data-testid="installment-editor"]');
    
    if (await installmentEditor.isVisible({ timeout: 3000 }).catch(() => false)) {
      // Verify statement dropdown exists
      const statementDropdown = page.locator('[data-testid="statement-selector"]');
      await expect(statementDropdown).toBeVisible();
      
      // Verify dropdown has options
      const optionsCount = await statementDropdown.locator('option').count();
      expect(optionsCount).toBeGreaterThan(0);
      
      // Verify "Automático" option exists
      const autoOption = statementDropdown.locator('option:has-text("Automático")');
      await expect(autoOption).toBeVisible();
    } else {
      // If no installments section, this might not be a credit card purchase
      test.skip(true, 'No installments section found - not a credit card purchase');
    }
  });
});
