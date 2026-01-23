/**
 * Currency Preference Context
 * 
 * Manages global currency preference (ARS/USD) with localStorage persistence.
 */

import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { ExchangeRateType } from '../../domain/entities/ExchangeRate';

export type Currency = 'ARS' | 'USD';

export interface CurrencyPreference {
  currency: Currency;
  preferredRateType: ExchangeRateType;
}

interface CurrencyContextValue {
  preference: CurrencyPreference;
  setPreference: (preference: CurrencyPreference) => void;
  toggleCurrency: () => void;
}

const CurrencyContext = createContext<CurrencyContextValue | undefined>(undefined);

const STORAGE_KEY = 'cashdata_currency_preference';

export function CurrencyProvider({ children }: { children: ReactNode }) {
  const [preference, setPreferenceState] = useState<CurrencyPreference>(() => {
    // Load from localStorage
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (error) {
      console.error('Failed to load currency preference:', error);
    }
    // Default preference
    return {
      currency: 'ARS',
      preferredRateType: 'blue',
    };
  });

  // Persist to localStorage when preference changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(preference));
    } catch (error) {
      console.error('Failed to save currency preference:', error);
    }
  }, [preference]);

  const setPreference = (newPreference: CurrencyPreference) => {
    setPreferenceState(newPreference);
  };

  const toggleCurrency = () => {
    setPreferenceState((prev) => ({
      ...prev,
      currency: prev.currency === 'ARS' ? 'USD' : 'ARS',
    }));
  };

  return (
    <CurrencyContext.Provider value={{ preference, setPreference, toggleCurrency }}>
      {children}
    </CurrencyContext.Provider>
  );
}

export function useCurrencyPreference() {
  const context = useContext(CurrencyContext);
  if (context === undefined) {
    throw new Error('useCurrencyPreference must be used within a CurrencyProvider');
  }
  return context;
}
