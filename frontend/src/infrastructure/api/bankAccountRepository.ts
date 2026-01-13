import type { BankAccount } from '../../domain/entities';
import type { IBankAccountRepository } from '../../domain/repositories';

export class BankAccountApiRepository implements IBankAccountRepository {
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
  }

  async findByUserId(userId: number): Promise<BankAccount[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/v1/bank-accounts?user_id=${userId}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch bank accounts');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching bank accounts:', error);
      throw error;
    }
  }

  /**
   * Crea una nueva cuenta bancaria
   * 
   * Backend endpoint: POST /api/v1/bank-accounts
   * Body: { primary_user_id, secondary_user_id?, name, bank, account_type, last_four_digits, currency }
   */
  async create(
    _userId: number,
    data: Omit<BankAccount, 'id' | 'payment_method_id'>
  ): Promise<BankAccount> {
    try {
      const requestBody = {
        primary_user_id: data.primary_user_id,
        secondary_user_id: data.secondary_user_id,
        name: data.name,
        bank: data.bank,
        account_type: data.account_type,
        last_four_digits: data.last_four_digits,
        currency: data.currency,
      };

      const response = await fetch(
        `${this.baseUrl}/api/v1/bank-accounts`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create bank account');
      }

      const createdAccount = await response.json();
      return createdAccount;
    } catch (error) {
      console.error('Error creating bank account:', error);
      throw error;
    }
  }

  /**
   * Elimina una cuenta bancaria
   * 
   * Backend endpoint: DELETE /api/v1/bank-accounts/{bank_account_id}
   */
  async delete(id: number, _userId: number): Promise<void> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/v1/bank-accounts/${id}`,
        {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete bank account');
      }

      return;
    } catch (error) {
      console.error('Error deleting bank account:', error);
      throw error;
    }
  }
}
