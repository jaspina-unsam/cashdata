import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { installmentRepository } from '../../infrastructure';

export function usePurchaseInstallmentsMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, userId, purchaseId: _purchaseId, data }: { id: number; userId: number; purchaseId: number; data: any }) =>
      installmentRepository.update(id, userId, data),
    onSuccess: (_, variables) => {
      // Invalidate purchases and statements to refresh related data
      queryClient.invalidateQueries({ queryKey: ['purchases'] });
      queryClient.invalidateQueries({ queryKey: ['statements'] });
      // Also invalidate the specific installments query for this purchase
      queryClient.invalidateQueries({ queryKey: ['purchases', variables.purchaseId, 'installments', variables.userId] });
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
