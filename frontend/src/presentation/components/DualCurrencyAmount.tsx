/**
 * Dual Currency Amount Component
 * 
 * Displays amount in both currencies with conversion.
 */

import { useCurrencyPreference } from '../../application/contexts/CurrencyContext';

interface DualCurrencyAmountProps {
  primaryAmount: number;
  primaryCurrency: string;
  secondaryAmount?: number;
  secondaryCurrency?: string;
  exchangeRate?: number;
  showBothAlways?: boolean;
  className?: string;
}

export function DualCurrencyAmount({
  primaryAmount,
  primaryCurrency,
  secondaryAmount,
  secondaryCurrency,
  exchangeRate,
  showBothAlways = false,
  className = '',
}: DualCurrencyAmountProps) {
  const { preference } = useCurrencyPreference();

  const formatAmount = (amount: number, currency: string) => {
    const formatted = amount.toLocaleString('es-AR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
    return currency === 'USD' ? `US$${formatted}` : `$${formatted}`;
  };

  // If showing both always (e.g., in statements)
  if (showBothAlways) {
    // Determine which is ARS and which is USD
    let arsAmount: number | undefined;
    let usdAmount: number | undefined;

    if (primaryCurrency === 'ARS') {
      arsAmount = primaryAmount;
      usdAmount = secondaryAmount;
    } else if (primaryCurrency === 'USD') {
      usdAmount = primaryAmount;
      arsAmount = secondaryAmount;
    } else if (secondaryCurrency === 'ARS') {
      arsAmount = secondaryAmount;
      usdAmount = primaryAmount;
    } else if (secondaryCurrency === 'USD') {
      usdAmount = secondaryAmount;
      arsAmount = primaryAmount;
    } else {
      // Default: primary is ARS
      arsAmount = primaryAmount;
    }

    return (
      <div className={`flex flex-col ${className}`}>
        <span className="font-medium">
          {arsAmount !== undefined ? formatAmount(arsAmount, 'ARS') : '-'}
        </span>
        <span className="text-gray-600 text-sm">
          {usdAmount !== undefined ? formatAmount(usdAmount, 'USD') : '-'}
        </span>
      </div>
    );
  }

  // Show based on preference
  const isShowingPrimary = preference.currency === primaryCurrency;

  if (isShowingPrimary) {
    // Show primary with optional secondary in parentheses
    return (
      <span className={className}>
        {formatAmount(primaryAmount, primaryCurrency)}
        {secondaryAmount && secondaryCurrency && (
          <span className="text-gray-500 text-sm ml-2">
            (≈ {formatAmount(secondaryAmount, secondaryCurrency)})
          </span>
        )}
      </span>
    );
  } else {
    // Show secondary (converted) or calculate from exchange rate
    if (secondaryAmount && secondaryCurrency) {
      return (
        <span className={className}>
          {formatAmount(secondaryAmount, secondaryCurrency)}
          <span className="text-gray-500 text-sm ml-2">
            (≈ {formatAmount(primaryAmount, primaryCurrency)})
          </span>
        </span>
      );
    } else if (exchangeRate) {
      // Calculate conversion
      const converted = primaryCurrency === 'USD' 
        ? primaryAmount * exchangeRate 
        : primaryAmount / exchangeRate;
      const convertedCurrency = primaryCurrency === 'USD' ? 'ARS' : 'USD';

      return (
        <span className={className}>
          {formatAmount(converted, convertedCurrency)}
          <span className="text-gray-500 text-sm ml-2">
            (≈ {formatAmount(primaryAmount, primaryCurrency)})
          </span>
        </span>
      );
    } else {
      // No conversion available, show primary
      return (
        <span className={`${className} text-gray-500`}>
          {formatAmount(primaryAmount, primaryCurrency)}
        </span>
      );
    }
  }
}
