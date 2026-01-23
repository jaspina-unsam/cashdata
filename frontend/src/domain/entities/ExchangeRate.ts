/**
 * Domain Entity: ExchangeRate
 * 
 * Represents an exchange rate between two currencies.
 */

export type ExchangeRateType = 'official' | 'blue' | 'mep' | 'ccl' | 'custom' | 'inferred';

export interface ExchangeRate {
  id: number;
  date: string; // Format: YYYY-MM-DD
  from_currency: string;
  to_currency: string;
  rate: number;
  rate_type: ExchangeRateType;
  source?: string;
  notes?: string;
  created_by_user_id?: number;
  created_at?: string;
}

export interface CreateExchangeRateData {
  date: string; // Format: YYYY-MM-DD
  from_currency: string;
  to_currency: string;
  rate: number;
  rate_type: ExchangeRateType;
  source?: string;
  notes?: string;
}
