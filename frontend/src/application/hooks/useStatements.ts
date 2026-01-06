/**
 * Application Hooks: Monthly Statements
 * 
 * React Query hooks for managing monthly statement data.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { MonthlyStatement, StatementDetail } from '../../domain/entities';
import { monthlyStatementRepository } from '../../infrastructure/api/monthlyStatementRepository';

/**
 * Hook to fetch all statements for a user
 */
export function useStatements(userId: number, includeFuture: boolean = false) {
  return useQuery({
    queryKey: ['statements', userId, includeFuture],
    queryFn: () => monthlyStatementRepository.findByUserId(userId, includeFuture),
    enabled: !!userId,
  });
}

/**
 * Hook to fetch a single statement detail with purchases
 */
export function useStatement(statementId: number, userId: number) {
  return useQuery({
    queryKey: ['statement', statementId, userId],
    queryFn: () => monthlyStatementRepository.findById(statementId, userId),
    enabled: !!statementId && !!userId,
  });
}

/**
 * Hook to create a new statement
 */
export function useCreateStatement() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      userId,
      data,
    }: {
      userId: number;
      data: {
        credit_card_id: number;
        closing_date: string;
        due_date: string;
      };
    }) => monthlyStatementRepository.create(userId, data),
    onSuccess: (_, variables) => {
      // Invalidate statements list for this user
      queryClient.invalidateQueries({
        queryKey: ['statements', variables.userId],
      });
    },
  });
}

/**
 * Hook to update statement dates
 */
export function useUpdateStatementDates() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      statementId,
      userId,
      data,
    }: {
      statementId: number;
      userId: number;
      data: {
        closing_date: string;
        due_date: string;
      };
    }) => monthlyStatementRepository.updateDates(statementId, userId, data),
    onSuccess: (_, variables) => {
      // Invalidate both the statement detail and the list
      queryClient.invalidateQueries({
        queryKey: ['statement', variables.statementId],
      });
      queryClient.invalidateQueries({
        queryKey: ['statements', variables.userId],
      });
    },
  });
}
