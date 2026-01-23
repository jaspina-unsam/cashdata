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
  page?: number;
  page_size?: number;
  startDate?: string; // Format: YYYY-MM-DD
  endDate?: string; // Format: YYYY-MM-DD
}

export interface PaginatedPurchases {
  items: Purchase[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * Hook to fetch all purchases for a user
 */
export function usePurchases(userId: number, filters?: PurchaseFilters) {
  return useQuery<PaginatedPurchases>({
    queryKey: queryKeys.purchases.all(userId, filters),
    queryFn: () =>
      purchaseRepository.findByUserId(userId, filters),
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
      purchaseRepository.findByCreditCardId(cardId, userId, filters?.page, filters?.page_size),
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
      purchaseRepository.findByCategoryId(categoryId, userId, filters?.page, filters?.page_size),
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
      if (variables.data.payment_method_id) {
        queryClient.invalidateQueries({
          queryKey: queryKeys.purchases.byCard(variables.data.payment_method_id, variables.userId),
        });
      }
      if (variables.data.category_id) {
        queryClient.invalidateQueries({
          queryKey: queryKeys.purchases.byCategory(variables.data.category_id, variables.userId),
        });
      }
      // Invalidate credit card summary to reflect new purchase
      if (variables.data.payment_method_id) {
        queryClient.invalidateQueries({
          queryKey: ['creditCards', variables.data.payment_method_id, 'summary'],
        });
      }
      // Invalidate statements since creating a purchase creates statements
      queryClient.invalidateQueries({
        queryKey: ['statements', variables.userId],
      });
    },
  });
}

/**
 * Hook to delete a purchase
 */
export function useDeletePurchase() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, userId }: { id: number; userId: number }) => 
      purchaseRepository.delete(id, userId),
    onSuccess: (_, variables) => {
      // Invalidate all relevant purchase queries
      queryClient.invalidateQueries({
        queryKey: queryKeys.purchases.all(variables.userId, undefined),
      });
      // Invalidate all credit card queries to reflect changes
      queryClient.invalidateQueries({
        queryKey: ['creditCards'],
      });
    },
  });
}

/**
 * Hook to update a purchase
 */
export function useUpdatePurchase() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, userId, data }: { id: number; userId: number; data: Partial<Omit<Purchase, 'id' | 'user_id'>> }) =>
      purchaseRepository.update(id, userId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.purchases.all(variables.userId, undefined) });
      queryClient.invalidateQueries({ queryKey: queryKeys.purchases.detail(variables.id, variables.userId) });
      // Invalidate statements and credit cards summaries
      queryClient.invalidateQueries({ queryKey: ['statements'] });
      queryClient.invalidateQueries({ queryKey: ['creditCards'] });
    },
  });
}
