/**
 * Category Hooks
 * 
 * React Query hooks for category operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { Category } from '../../domain/entities';
import { categoryRepository } from '../../infrastructure';
import { queryKeys } from '../config/queryClient';

/**
 * Hook to fetch all categories
 */
export function useCategories() {
  return useQuery({
    queryKey: queryKeys.categories.all,
    queryFn: () => categoryRepository.findAll(),
  });
}

/**
 * Hook to fetch a single category by ID
 */
export function useCategory(id: number) {
  return useQuery({
    queryKey: queryKeys.categories.detail(id),
    queryFn: () => categoryRepository.findById(id),
    enabled: !!id,
  });
}

/**
 * Hook to create a new category
 */
export function useCreateCategory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Omit<Category, 'id'>) => categoryRepository.create(data),
    onSuccess: () => {
      // Invalidate categories list to refetch
      queryClient.invalidateQueries({ queryKey: queryKeys.categories.all });
    },
  });
}
