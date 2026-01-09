import { httpClient } from '../http/httpClient';
import type { Installment } from '../../domain/entities';

export class InstallmentApiRepository {
  private readonly basePath = '/api/v1/installments';

  async update(id: number, userId: number, data: Partial<Installment>): Promise<Installment> {
    return httpClient.patch<Installment>(`${this.basePath}/${id}`, data, { user_id: userId });
  }

  async findByPurchase(purchaseId: number, userId: number): Promise<Installment[]> {
    return httpClient.get<Installment[]>(`/api/v1/purchases/${purchaseId}/installments`, { user_id: userId });
  }
}

export const installmentRepository = new InstallmentApiRepository();
