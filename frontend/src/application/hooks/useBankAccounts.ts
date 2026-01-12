import { useMutation, useQueryClient } from '@tanstack/react-query';
import { BankAccountApiRepository } from '../../infrastructure/api/bankAccountRepository';
import type { BankAccount } from '../../domain';

const bankAccountRepository = new BankAccountApiRepository();

export function useCreateBankAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, data }: { userId: number; data: Omit<BankAccount, 'id' | 'payment_method_id'> }) =>
      bankAccountRepository.create(userId, data),
    onSuccess: () => {
      // Invalidate and refetch payment methods since bank accounts are payment methods
      queryClient.invalidateQueries({ queryKey: ['paymentMethods'] });
    },
  });
}