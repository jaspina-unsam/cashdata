/**
 * API Repository: ExchangeRate
 * 
 * Implementation of IExchangeRateRepository using the HTTP API.
 */

import { httpClient } from '../http/httpClient';
import type { ExchangeRate, CreateExchangeRateData, ExchangeRateType } from '../../domain/entities/ExchangeRate';
import type { IExchangeRateRepository } from '../../domain/repositories/ExchangeRateRepository';

export class ExchangeRateApiRepository implements IExchangeRateRepository {
  private readonly basePath = '/api/v1/exchange-rates';

  async list(
    userId: number,
    filters?: {
      startDate?: string;
      endDate?: string;
      rateType?: ExchangeRateType;
      fromCurrency?: string;
      toCurrency?: string;
    }
  ): Promise<ExchangeRate[]> {
    // Backend requires start_date and end_date, so provide defaults if not specified
    const today = new Date().toISOString().split('T')[0];
    const oneYearAgo = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    return httpClient.get<ExchangeRate[]>(this.basePath, {
      user_id: userId,
      start_date: filters?.startDate || oneYearAgo,
      end_date: filters?.endDate || today,
      rate_type: filters?.rateType,
      from_currency: filters?.fromCurrency,
      to_currency: filters?.toCurrency,
    });
  }

  async getLatest(
    userId: number,
    rateType: ExchangeRateType,
    fromCurrency: string = 'USD',
    toCurrency: string = 'ARS'
  ): Promise<ExchangeRate | null> {
    try {
      return await httpClient.get<ExchangeRate>(`${this.basePath}/latest`, {
        user_id: userId,
        rate_type: rateType,
        from_currency: fromCurrency,
        to_currency: toCurrency,
      });
    } catch (error: any) {
      if (error.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async create(userId: number, data: CreateExchangeRateData): Promise<ExchangeRate> {
    return httpClient.post<ExchangeRate>(this.basePath, data, {
      user_id: userId,
    });
  }

  async delete(id: number, userId: number): Promise<void> {
    await httpClient.delete(`${this.basePath}/${id}`, {
      user_id: userId,
    });
  }
}

// Singleton instance
export const exchangeRateRepository = new ExchangeRateApiRepository();
