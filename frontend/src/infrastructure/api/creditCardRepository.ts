/**
 * API Repository: Credit Card
 * 
 * Implementation of ICreditCardRepository using the HTTP API.
 */

import { httpClient } from '../http/httpClient';
import type { CreditCard, CreditCardSummary } from '../../domain/entities';
import type { ICreditCardRepository } from '../../domain/repositories';

export class CreditCardApiRepository implements ICreditCardRepository {
  private readonly basePath = '/api/v1/credit-cards';

  async findByUserId(
    userId: number,
    skip: number = 0,
    limit: number = 100
  ): Promise<CreditCard[]> {
    return httpClient.get<CreditCard[]>(this.basePath, {
      user_id: userId,
      skip,
      limit,
    });
  }

  async findById(id: number, userId: number): Promise<CreditCard | null> {
    try {
      return await httpClient.get<CreditCard>(`${this.basePath}/${id}`, {
        user_id: userId,
      });
    } catch (error: any) {
      if (error.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async getSummary(
    id: number,
    userId: number,
    billingPeriod: string
  ): Promise<CreditCardSummary> {
    return httpClient.get<CreditCardSummary>(
      `${this.basePath}/${id}/summary`,
      {
        user_id: userId,
        billing_period: billingPeriod,
      }
    );
  }

  async create(
    userId: number,
    data: Omit<CreditCard, 'id' | 'user_id'>
  ): Promise<CreditCard> {
    return httpClient.post<CreditCard>(this.basePath, data, {
      user_id: userId,
    });
  }

  async delete(id: number, userId: number): Promise<void> {
    await httpClient.delete(`${this.basePath}/${id}`, {
      user_id: userId,
    });
  }
}

export const creditCardRepository = new CreditCardApiRepository();
