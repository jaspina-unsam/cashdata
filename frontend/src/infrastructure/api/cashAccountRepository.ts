import type { CashAccount } from '../../domain/entities';
import type { ICashAccountRepository } from '../../domain/repositories';

export class CashAccountApiRepository implements ICashAccountRepository {
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  }

  /**
   * Lista todas las cuentas de efectivo de un usuario
   *
   * Backend endpoint: GET /api/v1/cash-accounts/user/{user_id}
   */
  async findByUserId(userId: number): Promise<CashAccount[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/v1/cash-accounts/user/${userId}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch cash accounts');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching cash accounts:', error);
      throw error;
    }
  }

  /**
   * Crea una nueva cuenta de efectivo
   * 
   * Backend endpoint: POST /api/v1/cash-accounts
   * Body: { user_id, name, currency }
   */
  async create(
    userId: number,
    data: Omit<CashAccount, 'id' | 'payment_method_id' | 'user_id'>
  ): Promise<CashAccount> {
    try {
      // Preparar el body con los datos requeridos por el backend
      const requestBody = {
        user_id: userId,
        name: data.name,
        currency: data.currency,
      };

      const response = await fetch(
        `${this.baseUrl}/api/v1/cash-accounts`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody), // Convertir objeto a JSON string
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create cash account');
      }

      const createdAccount = await response.json();
      return createdAccount;
    } catch (error) {
      console.error('Error creating cash account:', error);
      throw error;
    }
  }

  /**
   * Elimina una cuenta de efectivo
   *
   * Backend endpoint: DELETE /api/v1/cash-accounts/{cash_account_id}
   */
  async delete(id: number, userId: number): Promise<void> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/v1/cash-accounts/${id}`,
        {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete cash account');
      }

      // DELETE no retorna datos, solo status 204
      return;
    } catch (error) {
      console.error('Error deleting cash account:', error);
      throw error;
    }
  }
}
