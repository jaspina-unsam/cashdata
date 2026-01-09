import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { installmentRepository } from '../../infrastructure';

export function usePurchaseInstallmentsMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, userId, data }: { id: number; userId: number; data: any }) =>
      installmentRepository.update(id, userId, data),
    onSuccess: () => {
      // Invalidate purchases and statements to refresh related data
      queryClient.invalidateQueries({ queryKey: ['purchases'] });
      queryClient.invalidateQueries({ queryKey: ['statements'] });
    },
  });
}

export function usePurchaseInstallments(purchaseId: number, userId: number) {
  return useQuery({
    queryKey: ['purchases', purchaseId, 'installments', userId],
    queryFn: () => installmentRepository.findByPurchase(purchaseId, userId),
    enabled: !!purchaseId && !!userId,
  });
}
