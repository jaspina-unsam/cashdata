/**
 * Exchange Rate Hooks
 * 
 * React Query hooks for exchange rate operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { CreateExchangeRateData, ExchangeRateType } from '../../domain/entities/ExchangeRate';
import { exchangeRateRepository } from '../../infrastructure/api/exchangeRatesApi';

export interface ExchangeRateFilters {
  startDate?: string; // Format: YYYY-MM-DD
  endDate?: string; // Format: YYYY-MM-DD
  rateType?: ExchangeRateType;
  fromCurrency?: string;
  toCurrency?: string;
}

/**
 * Hook to fetch exchange rates with filters
 */
export function useExchangeRates(userId: number, filters?: ExchangeRateFilters) {
  return useQuery({
    queryKey: ['exchangeRates', userId, filters],
    queryFn: () => exchangeRateRepository.list(userId, filters),
    enabled: !!userId,    keepPreviousData: true,  });
}

/**
 * Hook to fetch the latest exchange rate for a specific type
 */
export function useLatestRate(
  userId: number,
  rateType: ExchangeRateType,
  fromCurrency: string = 'USD',
  toCurrency: string = 'ARS'
) {
  return useQuery({
    queryKey: ['exchangeRates', 'latest', userId, rateType, fromCurrency, toCurrency],
    queryFn: () => exchangeRateRepository.getLatest(userId, rateType, fromCurrency, toCurrency),
    enabled: !!userId && !!rateType,
    keepPreviousData: true,
  });
}

/**
 * Hook to create a new exchange rate
 */
export function useCreateExchangeRate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, data }: { userId: number; data: CreateExchangeRateData }) =>
      exchangeRateRepository.create(userId, data),
    onSuccess: () => {
      // Invalidate all exchange rate queries
      queryClient.invalidateQueries({ queryKey: ['exchangeRates'] });
    },
  });
}

/**
 * Hook to delete an exchange rate
 */
export function useDeleteExchangeRate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, userId }: { id: number; userId: number }) =>
      exchangeRateRepository.delete(id, userId),
    onSuccess: () => {
      // Invalidate all exchange rate queries
      queryClient.invalidateQueries({ queryKey: ['exchangeRates'] });
    },
  });
}
