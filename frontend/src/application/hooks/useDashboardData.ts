import { useQuery } from '@tanstack/react-query';
import { dashboardRepository } from '../../infrastructure';
import { useActiveUser } from '../contexts/UserContext';
import { useCurrencyPreference } from '../contexts/CurrencyContext';
import type { DashboardMetrics, ExpensesByMonth, ExpensesByCategory, IncomesByMonth } from '../../domain/entities';

export function useDashboardMetrics(period: string = 'current-month') {
  const { activeUserId } = useActiveUser();
  const { preference } = useCurrencyPreference();
  const currency = preference.currency;

  return useQuery<DashboardMetrics>({
    queryKey: ['dashboard', 'metrics', activeUserId, currency, period],
    queryFn: () => dashboardRepository.getMetrics(activeUserId!, currency, period),
    enabled: !!activeUserId,
    keepPreviousData: true,
  });
}

export function useLatestBudget() {
  const { activeUserId } = useActiveUser();

  return useQuery({
    queryKey: ['budgets', 'latest', activeUserId],
    queryFn: () => dashboardRepository.getLatestBudget(activeUserId!),
    enabled: !!activeUserId,
    keepPreviousData: true,
  });
}

export function useUpcomingInstallments(months: number = 6) {
  const { activeUserId } = useActiveUser();
  const { preference } = useCurrencyPreference();
  const currency = preference.currency;

  return useQuery({
    queryKey: ['installments', 'upcoming', activeUserId, months, currency],
    queryFn: () => dashboardRepository.getUpcomingInstallments(activeUserId!, months, currency),
    enabled: !!activeUserId,
    keepPreviousData: true,
  });
}

export function useExpensesByMonth(months: number = 6) {
  const { activeUserId } = useActiveUser();
  const { preference } = useCurrencyPreference();
  const currency = preference.currency;

  return useQuery<ExpensesByMonth[]>({
    queryKey: ['analytics', 'expenses-by-month', activeUserId, currency, months],
    queryFn: () => dashboardRepository.getExpensesByMonth(activeUserId!, currency, months),
    enabled: !!activeUserId,
    keepPreviousData: true,
  });
}

export function useExpensesByCategory(months: number = 6) {
  const { activeUserId } = useActiveUser();
  const { preference } = useCurrencyPreference();
  const currency = preference.currency;

  return useQuery<ExpensesByCategory[]>({
    queryKey: ['analytics', 'expenses-by-category', activeUserId, currency, months],
    queryFn: () => dashboardRepository.getExpensesByCategory(activeUserId!, currency, months),
    enabled: !!activeUserId,
    keepPreviousData: true,
  });
}

export function useIncomesByMonth(months: number = 6) {
  const { activeUserId } = useActiveUser();
  const { preference } = useCurrencyPreference();
  const currency = preference.currency;

  return useQuery<IncomesByMonth[]>({
    queryKey: ['analytics', 'incomes-by-month', activeUserId, currency, months],
    queryFn: () => dashboardRepository.getIncomesByMonth(activeUserId!, currency, months),
    enabled: !!activeUserId,
    keepPreviousData: true,
  });
}
