import { httpClient } from '../http/httpClient';
import type { MonthlyStatement } from '../../domain/entities';

export class StatementsApiRepository {
  async findByCard(creditCardId: number, userId: number): Promise<MonthlyStatement[]> {
    return httpClient.get<MonthlyStatement[]>(`/api/v1/statements/by-card/${creditCardId}`, { user_id: userId });
  }
}

export const statementsRepository = new StatementsApiRepository();
