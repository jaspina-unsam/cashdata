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
    mutationFn: (data: Omit<Purchase, 'id'>) => purchaseRepository.create(data),
    onSuccess: (_, variables) => {
      // Invalidate all relevant purchase queries
      queryClient.invalidateQueries({
        queryKey: queryKeys.purchases.all(variables.user_id, undefined),
      });
      if (variables.credit_card_id) {
        queryClient.invalidateQueries({
          queryKey: queryKeys.purchases.byCard(variables.credit_card_id, variables.user_id),
        });
      }
      if (variables.category_id) {
        queryClient.invalidateQueries({
          queryKey: queryKeys.purchases.byCategory(variables.category_id, variables.user_id),
        });
      }
      // Invalidate credit card summary to reflect new purchase
      if (variables.credit_card_id) {
        queryClient.invalidateQueries({
          queryKey: ['creditCards', variables.credit_card_id, 'summary'],
        });
      }
    },
  });
}
