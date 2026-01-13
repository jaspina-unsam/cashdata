import type { DigitalWallet } from '../../domain/entities';
import type { IDigitalWalletRepository } from '../../domain/repositories';


export class DigitalWalletApiRepository implements IDigitalWalletRepository {
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
  }

    async findByUserId(userId: number): Promise<DigitalWallet[]> {
        try {
            const response = await fetch(
                `${this.baseUrl}/api/v1/digital-wallets?user_id=${userId}`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to fetch digital wallets");
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Error fetching digital wallets:", error);
            throw error;
        }
    }

    async create(
        userId: number,
        data: Omit<DigitalWallet, 'id' | 'payment_method_id' | 'user_id'>
    ): Promise<DigitalWallet> {
        try {
            const requestBody = {
                user_id: userId,
                name: data.name,
                provider: data.provider,
                currency: data.currency,
            };

            const response = await fetch(
                `${this.baseUrl}/api/v1/digital-wallets`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(requestBody)
                }
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to create digital wallet");
            }

            const responseData = await response.json();
            return responseData;
        } catch (error) {
            console.error("Error creating digital wallet:", error);
            throw error;
        }
    }

    async delete(id: number, userId: number): Promise<void> {
        try {
            const response = await fetch(
                `${this.baseUrl}/api/v1/digital-wallets/${id}?user_id=${userId}`,
                {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to delete digital wallet");
            }

            return;
        } catch (error) {
            console.error("Error deleting digital wallet:", error);
            throw error;
        }
    }
}