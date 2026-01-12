import { useMutation, useQueryClient } from '@tanstack/react-query';
import { DigitalWalletApiRepository } from '../../infrastructure/api/digitalWalletRepository';
import type { DigitalWallet } from '../../domain';

const digitalWalletRepository = new DigitalWalletApiRepository();

export function useCreateDigitalWallet() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, data }: { userId: number; data: Omit<DigitalWallet, 'id' | 'payment_method_id' | 'user_id'> }) =>
      digitalWalletRepository.create(userId, data),
    onSuccess: () => {
      // Invalidate and refetch payment methods since digital wallets are payment methods
      queryClient.invalidateQueries({ queryKey: ['paymentMethods'] });
    },
  });
}