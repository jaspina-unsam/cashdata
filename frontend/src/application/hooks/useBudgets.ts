import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { budgetsRepository } from '../../infrastructure/api/budgetsRepository';
import type { CreateBudgetData, AddExpenseData, UpdateResponsibilitiesData } from '../../infrastructure/api/budgetsRepository';
import type { MonthlyBudget, BudgetDetails } from '../../domain/entities';

// Query keys
export const budgetKeys = {
  all: ['budgets'] as const,
  lists: () => [...budgetKeys.all, 'list'] as const,
  list: (period: string, userId: number) => [...budgetKeys.lists(), { period, userId }] as const,
  details: () => [...budgetKeys.all, 'detail'] as const,
  detail: (budgetId: number) => [...budgetKeys.details(), budgetId] as const,
};

// List budgets by period
export function useBudgets(period: string, userId: number) {
  return useQuery({
    queryKey: budgetKeys.list(period, userId),
    queryFn: () => budgetsRepository.listByPeriod(period, userId),
    enabled: !!period && !!userId,
  });
}

// Get budget details
export function useBudgetDetails(budgetId: number | undefined, userId: number) {
  return useQuery({
    queryKey: budgetKeys.detail(budgetId!),
    queryFn: () => budgetsRepository.getDetails(budgetId!, userId),
    enabled: !!budgetId && !!userId,
  });
}

// Create budget
export function useCreateBudget() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateBudgetData) => budgetsRepository.create(data),
    onSuccess: (newBudget) => {
      // Invalidate all budget lists that might include this period
      queryClient.invalidateQueries({ queryKey: budgetKeys.lists() });
    },
  });
}

// Add expense to budget
export function useAddExpense() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AddExpenseData) => budgetsRepository.addExpense(data.budget_id, data),
    onSuccess: (_, variables) => {
      // Invalidate budget details to refetch with new expense
      queryClient.invalidateQueries({ queryKey: budgetKeys.detail(variables.budget_id) });
    },
  });
}

// Update expense responsibilities
export function useUpdateResponsibilities() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ budgetId, expenseId, data }: { budgetId: number; expenseId: number; data: UpdateResponsibilitiesData }) =>
      budgetsRepository.updateResponsibilities(budgetId, expenseId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: budgetKeys.detail(variables.budgetId) });
    },
  });
}

// Remove expense from budget
export function useRemoveExpense() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ budgetId, expenseId, userId }: { budgetId: number; expenseId: number; userId: number }) =>
      budgetsRepository.removeExpense(budgetId, expenseId, userId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: budgetKeys.detail(variables.budgetId) });
    },
  });
}
