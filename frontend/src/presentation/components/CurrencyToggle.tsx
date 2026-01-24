/**
 * Currency Toggle Component
 * 
 * Switch between ARS and USD with latest exchange rate display.
 */

import { DollarSign, TrendingUp } from 'lucide-react';
import { useCurrencyPreference } from '../../application/contexts/CurrencyContext';
import { useLatestRate } from '../../application/hooks/useExchangeRates';
import { useActiveUser } from '../../application/contexts/UserContext';

export function CurrencyToggle() {
  const { preference, toggleCurrency } = useCurrencyPreference();
  const { activeUserId } = useActiveUser();

  const { data: latestRate } = useLatestRate(
    activeUserId,
    preference.preferredRateType,
    'USD',
    'ARS'
  );

  return (
    <div className="flex items-center gap-4">
      {/* Exchange Rate Display */}
      {latestRate && (
        <div className="flex items-center gap-2 text-white text-sm">
          <TrendingUp size={16} />
          <span>
            ${latestRate.rate.toLocaleString('es-AR', { minimumFractionDigits: 2 })}
          </span>
        </div>
      )}

      {/* Toggle Button */}
      <button
        onClick={toggleCurrency}
        className="relative inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 rounded-full px-4 py-2 transition-colors"
        title={`Cambiar a ${preference.currency === 'ARS' ? 'USD' : 'ARS'}`}
      >
        <DollarSign size={18} className="text-white" />
        <span className="text-white font-medium">{preference.currency}</span>
      </button>
    </div>
  );
}
