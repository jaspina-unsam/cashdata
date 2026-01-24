import { useQuery } from '@tanstack/react-query';
import { PaymentMethodApiRepository } from '../../infrastructure/api/paymentMethodsRepository';
import type { PaymentMethod } from '../../domain';

const paymentMethodRepository = new PaymentMethodApiRepository();

export function usePaymentMethods(userId: number) {
  return useQuery<PaymentMethod[]>({
    queryKey: ['paymentMethods', userId],
    queryFn: () => paymentMethodRepository.findByUserId(userId),
    enabled: !!userId,
    keepPreviousData: true,
  });
}

export function useAllPaymentMethods() {
  return useQuery<PaymentMethod[]>({
    queryKey: ['paymentMethods', 'all'],
    queryFn: () => paymentMethodRepository.findAll(),
  });
}
