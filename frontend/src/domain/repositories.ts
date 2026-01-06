/**
 * Domain Repository Interfaces
 * 
 * Define contracts for data access without implementation details.
 * These interfaces ensure the domain layer is independent of infrastructure.
 */

import type { 
  Category, 
  CreditCard, 
  Purchase, 
  Installment, 
  CreditCardSummary,
  MonthlyStatement,
  StatementDetail
} from './entities';

/**
 * Repository interface for Category operations
 */
export interface ICategoryRepository {
  findAll(): Promise<Category[]>;
  findById(id: number): Promise<Category | null>;
  create(data: Omit<Category, 'id'>): Promise<Category>;
}

/**
 * Repository interface for Credit Card operations
 */
export interface ICreditCardRepository {
  findByUserId(userId: number, skip?: number, limit?: number): Promise<CreditCard[]>;
  findById(id: number, userId: number): Promise<CreditCard | null>;
  getSummary(id: number, userId: number, billingPeriod: string): Promise<CreditCardSummary>;
  create(userId: number, data: Omit<CreditCard, 'id' | 'user_id'>): Promise<CreditCard>;
  delete(id: number, userId: number): Promise<void>;
}

/**
 * Repository interface for Purchase operations
 */
export interface IPurchaseRepository {
  findByUserId(
    userId: number,
    filters?: { startDate?: string; endDate?: string; skip?: number; limit?: number }
  ): Promise<Purchase[]>;
  findById(id: number, userId: number): Promise<Purchase | null>;
  findByCreditCardId(cardId: number, userId: number, skip?: number, limit?: number): Promise<Purchase[]>;
  findByCategoryId(categoryId: number, userId: number, skip?: number, limit?: number): Promise<Purchase[]>;
  getInstallments(purchaseId: number, userId: number): Promise<Installment[]>;
  create(
    userId: number,
    data: Omit<Purchase, 'id' | 'user_id'>
  ): Promise<Purchase>;
  delete(id: number, userId: number): Promise<void>;
}

/**
 * Repository interface for Monthly Statement operations
 */
export interface IMonthlyStatementRepository {
  findByUserId(userId: number, includeFuture?: boolean): Promise<MonthlyStatement[]>;
  findById(statementId: number, userId: number): Promise<StatementDetail | null>;
  create(userId: number, data: {
    credit_card_id: number;
    closing_date: string;
    due_date: string;
  }): Promise<MonthlyStatement>;
  updateDates(statementId: number, userId: number, data: {
    closing_date: string;
    due_date: string;
  }): Promise<MonthlyStatement>;
}
