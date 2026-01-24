/**
 * Credit Card Hooks
 * 
 * React Query hooks for credit card operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { CreditCard, CreditCardSummary } from '../../domain/entities';
import { creditCardRepository } from '../../infrastructure';
import { queryKeys } from '../config/queryClient';

export interface CreditCardFilters {
  skip?: number;
  limit?: number;
}

export interface CreditCardSummaryParams {
  cardId: number;
  userId: number;
  billingPeriod: string; // Format: YYYY-MM
}

/**
 * Hook to fetch all credit cards for a user
 */
export function useCreditCards(userId: number, filters?: CreditCardFilters) {
  return useQuery<CreditCard[]>({
    queryKey: queryKeys.creditCards.all(userId),
    queryFn: () => creditCardRepository.findByUserId(userId, filters?.skip, filters?.limit),
    enabled: !!userId,
    keepPreviousData: true,
  });
}

/**
 * Hook to fetch a single credit card by ID
 */
export function useCreditCard(id: number, userId: number) {
  return useQuery<CreditCard | null>({
    queryKey: queryKeys.creditCards.detail(id, userId),
    queryFn: () => creditCardRepository.findById(id, userId),
    enabled: !!id && !!userId,
    keepPreviousData: true,
  });
}

/**
 * Hook to fetch credit card summary for a billing period
 */
export function useCreditCardSummary(params: CreditCardSummaryParams) {
  return useQuery<CreditCardSummary>({
    queryKey: queryKeys.creditCards.summary(params.cardId, params.userId, params.billingPeriod),
    queryFn: () =>
      creditCardRepository.getSummary(params.cardId, params.userId, params.billingPeriod),
    enabled: !!params.cardId && !!params.userId && !!params.billingPeriod,
  });
}

/**
 * Hook to create a new credit card
 */
export function useCreateCreditCard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, data }: { userId: number; data: Omit<CreditCard, 'id' | 'user_id'> }) => 
      creditCardRepository.create(userId, data),
    onSuccess: (_, variables) => {
      // Invalidate credit cards list for this user
      queryClient.invalidateQueries({
        queryKey: queryKeys.creditCards.all(variables.userId),
      });
    },
  });
}

/**
 * Hook to delete a credit card
 */
export function useDeleteCreditCard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, userId }: { id: number; userId: number }) => 
      creditCardRepository.delete(id, userId),
    onSuccess: (_, variables) => {
      // Invalidate credit cards list for this user
      queryClient.invalidateQueries({
        queryKey: queryKeys.creditCards.all(variables.userId),
      });
    },
  });
}
