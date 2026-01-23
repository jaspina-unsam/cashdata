/**
 * Domain Repository Interface: ExchangeRate
 * 
 * Contract for exchange rate data access.
 */

import type { ExchangeRate, CreateExchangeRateData, ExchangeRateType } from '../entities/ExchangeRate';

export interface IExchangeRateRepository {
  /**
   * List exchange rates within a date range
   */
  list(
    userId: number,
    filters?: {
      startDate?: string;
      endDate?: string;
      rateType?: ExchangeRateType;
      fromCurrency?: string;
      toCurrency?: string;
    }
  ): Promise<ExchangeRate[]>;

  /**
   * Get latest exchange rate for a specific type
   */
  getLatest(
    userId: number,
    rateType: ExchangeRateType,
    fromCurrency?: string,
    toCurrency?: string
  ): Promise<ExchangeRate | null>;

  /**
   * Create new exchange rate
   */
  create(userId: number, data: CreateExchangeRateData): Promise<ExchangeRate>;

  /**
   * Delete exchange rate
   */
  delete(id: number, userId: number): Promise<void>;
}
