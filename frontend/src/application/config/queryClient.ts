/**
 * React Query Configuration
 * 
 * Global configuration for TanStack Query (React Query).
 */

import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
});

/**
 * Query Keys
 * 
 * Centralized query key factory for consistent cache management.
 */
export const queryKeys = {
  categories: {
    all: ['categories'] as const,
    detail: (id: number) => ['categories', id] as const,
  },
  creditCards: {
    all: (userId: number) => ['creditCards', userId] as const,
    detail: (id: number, userId: number) => ['creditCards', id, userId] as const,
    summary: (id: number, userId: number, billingPeriod: string) =>
      ['creditCards', id, 'summary', billingPeriod, userId] as const,
  },
  purchases: {
    all: (userId: number, filters?: any) =>
      ['purchases', userId, filters] as const,
    detail: (id: number, userId: number) => ['purchases', id, userId] as const,
    installments: (id: number, userId: number) =>
      ['purchases', id, 'installments', userId] as const,
    byCard: (cardId: number, userId: number) =>
      ['purchases', 'byCard', cardId, userId] as const,
    byCategory: (categoryId: number, userId: number) =>
      ['purchases', 'byCategory', categoryId, userId] as const,
  },
} as const;
