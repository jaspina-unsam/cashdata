/**
 * API Repository: Purchase
 * 
 * Implementation of IPurchaseRepository using the HTTP API.
 */

import { httpClient } from '../http/httpClient';
import type { Purchase, Installment } from '../../domain/entities';
import type { IPurchaseRepository } from '../../domain/repositories';

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export class PurchaseApiRepository implements IPurchaseRepository {
  private readonly basePath = '/api/v1/purchases';

  async findByUserId(
    userId: number,
    filters?: { startDate?: string; endDate?: string; page?: number; page_size?: number }
  ): Promise<PaginatedResponse<Purchase>> {
    return httpClient.get<PaginatedResponse<Purchase>>(this.basePath, {
      user_id: userId,
      start_date: filters?.startDate,
      end_date: filters?.endDate,
      page: filters?.page || 1,
      page_size: filters?.page_size || 50,
    });
  }

  async findById(id: number, userId: number): Promise<Purchase | null> {
    try {
      return await httpClient.get<Purchase>(`${this.basePath}/${id}`, {
        user_id: userId,
      });
    } catch (error: any) {
      if (error.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async findByCreditCardId(
    cardId: number,
    userId: number,
    skip: number = 0,
    limit: number = 100
  ): Promise<Purchase[]> {
    return httpClient.get<Purchase[]>(`/api/v1/credit-cards/${cardId}/purchases`, {
      user_id: userId,
      skip,
      limit,
    });
  }

  async findByCategoryId(
    categoryId: number,
    userId: number,
    skip: number = 0,
    limit: number = 100
  ): Promise<Purchase[]> {
    return httpClient.get<Purchase[]>(`/api/v1/categories/${categoryId}/purchases`, {
      user_id: userId,
      skip,
      limit,
    });
  }

  async getInstallments(purchaseId: number, userId: number): Promise<Installment[]> {
    return httpClient.get<Installment[]>(`${this.basePath}/${purchaseId}/installments`, {
      user_id: userId,
    });
  }

  async create(
    userId: number,
    data: Omit<Purchase, 'id' | 'user_id'>
  ): Promise<Purchase> {
    return httpClient.post<Purchase>(this.basePath, data, {
      user_id: userId,
    });
  }

  async update(id: number, userId: number, data: Partial<Omit<Purchase, 'id' | 'user_id'>>): Promise<Purchase> {
    return httpClient.patch<Purchase>(`${this.basePath}/${id}`, data, {
      user_id: userId,
    });
  }

  async delete(id: number, userId: number): Promise<void> {
    await httpClient.delete(`${this.basePath}/${id}`, {
      user_id: userId,
    });
  }
}

export const purchaseRepository = new PurchaseApiRepository();
