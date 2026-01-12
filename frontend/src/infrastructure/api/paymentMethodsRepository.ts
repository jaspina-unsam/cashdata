import type { PaymentMethod, IPaymentMethodRepository } from "../../domain";


export class PaymentMethodApiRepository implements IPaymentMethodRepository {
    private baseUrl: string;

    constructor() {
        this.baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    }

    async findByUserId(userId: number): Promise<PaymentMethod[]> {
        try {
            const response = await fetch(
                `${this.baseUrl}/api/v1/payment-methods?user_id=${userId}`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to fetch payment methods");
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Error fetching payment methods:", error);
            throw error;
        }
    }

    async findById(id: number, userId: number): Promise<PaymentMethod | null> {
        try {
            const response = await fetch(
                `${this.baseUrl}/api/v1/payment-methods/${id}?user_id=${userId}`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            );
            if (!response.ok) {
                if (response.status === 404) {
                    return null;
                }
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to fetch payment method");
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Error fetching payment method:", error);
            throw error;
        }
    }
}