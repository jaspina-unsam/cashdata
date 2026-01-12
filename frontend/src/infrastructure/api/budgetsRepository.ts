import { httpClient } from '../http/httpClient';
import type { MonthlyBudget, BudgetDetails } from '../../domain/entities';

export interface CreateBudgetData {
  name: string;
  year: number;
  month: number;
  description?: string;
  created_by_user_id: number;
  participant_user_ids: number[];
}

export interface AddExpenseData {
  budget_id: number;
  purchase_id?: number;
  installment_id?: number;
  split_type: 'equal' | 'proportional' | 'custom' | 'full_single';
  custom_percentages?: Record<number, number>; // {user_id: percentage}
  responsible_user_id?: number; // For full_single
  requesting_user_id: number;
}

export interface UpdateResponsibilitiesData {
  budget_expense_id: number;
  split_type: 'equal' | 'proportional' | 'custom' | 'full_single';
  custom_percentages?: Record<number, number>;
  responsible_user_id?: number;
  requesting_user_id: number;
}

export class BudgetsApiRepository {
  private readonly baseUrl = '/api/v1/budgets';

  async create(data: CreateBudgetData): Promise<MonthlyBudget> {
    return httpClient.post<MonthlyBudget>(this.baseUrl, data);
  }

  async listByPeriod(period: string, userId: number): Promise<MonthlyBudget[]> {
    return httpClient.get<MonthlyBudget[]>(this.baseUrl, {
      period,
      user_id: userId,
    });
  }

  async getDetails(budgetId: number, userId: number): Promise<BudgetDetails> {
    return httpClient.get<BudgetDetails>(`${this.baseUrl}/${budgetId}`, {
      user_id: userId,
    });
  }

  async addExpense(budgetId: number, data: AddExpenseData): Promise<{budget_expense_id: number; success: boolean}> {
    return httpClient.post<{budget_expense_id: number; success: boolean}>(
      `${this.baseUrl}/${budgetId}/expenses`,
      data
    );
  }

  async updateResponsibilities(
    budgetId: number,
    expenseId: number,
    data: UpdateResponsibilitiesData
  ): Promise<{success: boolean}> {
    return httpClient.patch<{success: boolean}>(
      `${this.baseUrl}/${budgetId}/expenses/${expenseId}`,
      data
    );
  }

  async removeExpense(budgetId: number, expenseId: number, userId: number): Promise<void> {
    return httpClient.delete(
      `${this.baseUrl}/${budgetId}/expenses/${expenseId}`,
      { user_id: userId }
    );
  }
}

export const budgetsRepository = new BudgetsApiRepository();
