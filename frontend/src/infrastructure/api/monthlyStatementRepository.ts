/**
 * API Repository: Monthly Statements
 * 
 * Implements the IMonthlyStatementRepository interface using the HTTP client.
 */

import type { IMonthlyStatementRepository } from '../../domain/repositories';
import type { MonthlyStatement, StatementDetail } from '../../domain/entities';
import { httpClient } from '../http/httpClient';

export class ApiMonthlyStatementRepository implements IMonthlyStatementRepository {
  private readonly baseUrl = '/api/v1/statements';

  async findByUserId(userId: number, includeFuture: boolean = false): Promise<MonthlyStatement[]> {
    return httpClient.get<MonthlyStatement[]>(this.baseUrl, {
      user_id: userId,
      include_future: includeFuture
    });
  }

  async findById(statementId: number, userId: number): Promise<StatementDetail | null> {
    try {
      return await httpClient.get<StatementDetail>(
        `${this.baseUrl}/${statementId}`,
        { user_id: userId }
      );
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async create(
    userId: number,
    data: {
      credit_card_id: number;
      closing_date: string;
      due_date: string;
    }
  ): Promise<MonthlyStatement> {
    return httpClient.post<MonthlyStatement>(
      this.baseUrl,
      data,
      { user_id: userId }
    );
  }

  async updateDates(
    statementId: number,
    userId: number,
    data: {
      closing_date: string;
      due_date: string;
    }
  ): Promise<MonthlyStatement> {
    return httpClient.put<MonthlyStatement>(
      `${this.baseUrl}/${statementId}`,
      data,
      { user_id: userId }
    );
  }
}

// Export a singleton instance
export const monthlyStatementRepository = new ApiMonthlyStatementRepository();
