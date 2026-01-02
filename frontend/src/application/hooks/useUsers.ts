/**
 * User Hooks
 * 
 * React Query hooks for user operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { User } from '../../domain/entities';
import { userRepository } from '../../infrastructure';

/**
 * Hook to fetch all users
 */
export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => userRepository.findAll(),
  });
}

/**
 * Hook to fetch a single user by ID
 */
export function useUser(id: number) {
  return useQuery({
    queryKey: ['users', id],
    queryFn: () => userRepository.findById(id),
    enabled: !!id,
  });
}

/**
 * Hook to create a new user
 */
export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Omit<User, 'id'>) => userRepository.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

/**
 * Hook to update an existing user
 */
export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Omit<User, 'id'>> }) =>
      userRepository.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['users', variables.id] });
    },
  });
}

/**
 * Hook to delete a user
 */
export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => userRepository.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}
