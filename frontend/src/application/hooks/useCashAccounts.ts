import { useMutation, useQueryClient } from '@tanstack/react-query';
import { CashAccountApiRepository } from '../../infrastructure/api/cashAccountRepository';
import type { CashAccount } from '../../domain';

const cashAccountRepository = new CashAccountApiRepository();

export function useCreateCashAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, data }: { userId: number; data: Omit<CashAccount, 'id' | 'payment_method_id' | 'user_id'> }) =>
      cashAccountRepository.create(userId, data),
    onSuccess: () => {
      // Invalidate and refetch payment methods since cash accounts are payment methods
      queryClient.invalidateQueries({ queryKey: ['paymentMethods'] });
    },
  });
}