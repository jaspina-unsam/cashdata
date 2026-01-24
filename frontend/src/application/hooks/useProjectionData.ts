/**
 * Hook: useUserData
 * 
 * Fetches user data and recent purchases for projection calculations.
 * Calculates average monthly expenses from historical purchases.
 */

import { useQuery } from '@tanstack/react-query';
import { userRepository } from '../../infrastructure/api/userRepository';
import { PurchaseApiRepository } from '../../infrastructure/api/purchaseRepository';
import { useActiveUser } from '../contexts/UserContext';
import type { User, Purchase } from '../../domain/entities';
import type { ExchangeRate } from '../../domain/entities/ExchangeRate';

const purchaseRepository = new PurchaseApiRepository();

interface CalculatedExpenses {
  fixed: number;
  variable: number;
  total: number;
}

export function useUserData(userId?: number) {
  // Prefer explicit param, otherwise use active user from context
  const { activeUserId } = useActiveUser();
  const idToUse = userId ?? activeUserId;

  // Fetch user data
  const userQuery = useQuery<User | null>({
    queryKey: ['user', idToUse],
    queryFn: () => userRepository.findById(idToUse),
    enabled: !!idToUse,
    keepPreviousData: true,
  });
  
  // Fetch recent purchases (last 6 months)
  const sixMonthsAgo = new Date();
  sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
  
  const purchasesQuery = useQuery<Purchase[]>({
    queryKey: ['purchases', idToUse, 'recent-6m'],
    queryFn: async () => {
      const result = await purchaseRepository.findByUserId(idToUse, {
        startDate: sixMonthsAgo.toISOString().split('T')[0],
        endDate: new Date().toISOString().split('T')[0],
        page: 1,
        page_size: 500, // Get all purchases in the period
      });
      return result.items;
    },
    enabled: !!userQuery.data,
    keepPreviousData: true,
  });
  
  return {
    user: userQuery.data,
    purchases: purchasesQuery.data || [],
    isLoading: userQuery.isLoading || purchasesQuery.isLoading,
    error: userQuery.error || purchasesQuery.error,
  };
}

/**
 * Hook: useLatestExchangeRate
 * 
 * Fetches the latest exchange rate for a specific type (default: blue).
 * Used to convert ARS amounts to USD.
 */

import { ExchangeRateApiRepository } from '../../infrastructure/api/exchangeRatesApi';

const exchangeRateRepository = new ExchangeRateApiRepository();

export function useLatestExchangeRate(
  userId: number,
  rateType: 'official' | 'blue' | 'mep' | 'ccl' | 'custom' = 'blue'
) {
  return useQuery<ExchangeRate | null>({
    queryKey: ['exchange-rate', 'latest', rateType, userId],
    queryFn: () => exchangeRateRepository.getLatest(userId, rateType, 'USD', 'ARS'),
    staleTime: 1000 * 60 * 60, // 1 hour
    retry: 1, // Don't retry too much if rate doesn't exist
    keepPreviousData: true,
  });
}

/**
 * Helper: Calculate expenses from purchases
 * 
 * Converts all purchases to USD and calculates monthly average.
 * Uses heuristic: 60% fixed, 40% variable.
 */
export function calculateExpensesFromPurchases(
  purchases: any[], 
  latestRate: number | null
): CalculatedExpenses | null {
  if (!purchases.length || !latestRate) return null;
  
  // Sum all purchases in USD
  const totalUSD = purchases.reduce((sum, p) => {
    let amountUSD = p.total_amount;
    if (p.total_currency === 'ARS') {
      amountUSD = p.total_amount / latestRate;
    }
    return sum + amountUSD;
  }, 0);
  
  // Calculate monthly average (assuming 6 months of data)
  const monthsCount = 6;
  const avgMonthly = totalUSD / monthsCount;
  
  // Heuristic: 60% fixed expenses, 40% variable
  return {
    fixed: avgMonthly * 0.6,
    variable: avgMonthly * 0.4,
    total: avgMonthly,
  };
}
