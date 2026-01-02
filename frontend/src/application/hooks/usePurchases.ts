/**
 * Purchase Hooks
 * 
 * React Query hooks for purchase operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { Purchase } from '../../domain/entities';
import { purchaseRepository } from '../../infrastructure';
import { queryKeys } from '../config/queryClient';

export interface PurchaseFilters {
  skip?: number;
  limit?: number;
  startDate?: string; // Format: YYYY-MM-DD
  endDate?: string; // Format: YYYY-MM-DD
}

/**
 * Hook to fetch all purchases for a user
 */
export function usePurchases(userId: number, filters?: PurchaseFilters) {
  return useQuery({
    queryKey: queryKeys.purchases.all(userId, filters),
    queryFn: () =>
      purchaseRepository.findByUserId(
        userId,
        filters?.skip,
        filters?.limit,
        filters?.startDate,
        filters?.endDate
      ),
    enabled: !!userId,
  });
}

/**
 * Hook to fetch a single purchase by ID
 */
export function usePurchase(id: number, userId: number) {
  return useQuery({
    queryKey: queryKeys.purchases.detail(id, userId),
    queryFn: () => purchaseRepository.findById(id, userId),
    enabled: !!id && !!userId,
  });
}

/**
 * Hook to fetch purchases by credit card
 */
export function usePurchasesByCreditCard(
  cardId: number,
  userId: number,
  filters?: Omit<PurchaseFilters, 'startDate' | 'endDate'>
) {
  return useQuery({
    queryKey: queryKeys.purchases.byCard(cardId, userId),
    queryFn: () =>
      purchaseRepository.findByCreditCardId(cardId, userId, filters?.skip, filters?.limit),
    enabled: !!cardId && !!userId,
  });
}

/**
 * Hook to fetch purchases by category
 */
export function usePurchasesByCategory(
  categoryId: number,
  userId: number,
  filters?: Omit<PurchaseFilters, 'startDate' | 'endDate'>
) {
  return useQuery({
    queryKey: queryKeys.purchases.byCategory(categoryId, userId),
    queryFn: () =>
      purchaseRepository.findByCategoryId(categoryId, userId, filters?.skip, filters?.limit),
    enabled: !!categoryId && !!userId,
  });
}

/**
 * Hook to fetch installments for a purchase
 */
export function usePurchaseInstallments(purchaseId: number, userId: number) {
  return useQuery({
    queryKey: queryKeys.purchases.installments(purchaseId, userId),
    queryFn: () => purchaseRepository.getInstallments(purchaseId, userId),
    enabled: !!purchaseId && !!userId,
  });
}

/**
 * Hook to create a new purchase
 */
export function useCreatePurchase() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, data }: { userId: number; data: Omit<Purchase, 'id' | 'user_id'> }) => 
      purchaseRepository.create(userId, data),
    onSuccess: (_, variables) => {
      // Invalidate all relevant purchase queries
      queryClient.invalidateQueries({
        queryKey: queryKeys.purchases.all(variables.userId, undefined),
      });
      if (variables.data.credit_card_id) {
        queryClient.invalidateQueries({
          queryKey: queryKeys.purchases.byCard(variables.data.credit_card_id, variables.userId),
        });
      }
      if (variables.data.category_id) {
        queryClient.invalidateQueries({
          queryKey: queryKeys.purchases.byCategory(variables.data.category_id, variables.userId),
        });
      }
      // Invalidate credit card summary to reflect new purchase
      if (variables.data.credit_card_id) {
        queryClient.invalidateQueries({
          queryKey: ['creditCards', variables.data.credit_card_id, 'summary'],
        });
      }
    },
  });
}
