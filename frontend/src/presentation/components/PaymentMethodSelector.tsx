import React from 'react';
import { usePaymentMethods } from '../../application/hooks/usePaymentMethods';
import type { PaymentMethod } from '../../domain';

interface PaymentMethodSelectorProps {
  userId: number;
  value: number | null;
  onChange: (paymentMethodId: number) => void;
  onlyTypes?: string[];
}

export const PaymentMethodSelector: React.FC<PaymentMethodSelectorProps> = ({
  userId,
  value,
  onChange,
  onlyTypes
}) => {
  const { data: paymentMethods, isLoading, error } = usePaymentMethods(userId);

  const getIcon = (type: string) => {
    switch (type) {
      case 'credit_card':
        return '💳';
      case 'cash':
        return '💵';
      case 'bank_account':
        return '🏦';
      case 'digital_wallet':
        return '📱';
      default:
        return '💳';
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'credit_card':
        return 'Tarjetas de Crédito';
      case 'cash':
        return 'Efectivo';
      case 'bank_account':
        return 'Cuentas Bancarias';
      case 'digital_wallet':
        return 'Billeteras Digitales';
      default:
        return type;
    }
  };

  // Filter and group payment methods by type
  const groupedMethods = React.useMemo(() => {
    if (!paymentMethods) return {};

    const filtered = onlyTypes
      ? paymentMethods.filter(pm => onlyTypes.includes(pm.type))
      : paymentMethods;

    return filtered.reduce((groups, method) => {
      if (!groups[method.type]) {
        groups[method.type] = [];
      }
      groups[method.type].push(method);
      return groups;
    }, {} as Record<string, PaymentMethod[]>);
  }, [paymentMethods, onlyTypes]);

  if (isLoading) {
    return (
      <div className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50">
        <span className="text-gray-500">Cargando métodos de pago...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full px-4 py-2 border border-red-300 rounded-lg bg-red-50">
        <span className="text-red-500">Error al cargar métodos de pago</span>
      </div>
    );
  }

  return (
    <select
      value={value || ''}
      onChange={(e) => onChange(Number(e.target.value))}
      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      required
    >
      <option value="">Seleccionar método de pago</option>
      {Object.entries(groupedMethods).map(([type, methods]) => (
        <optgroup key={type} label={getTypeLabel(type)}>
          {methods.map((method) => (
            <option key={method.id} value={method.id}>
              {getIcon(method.type)} {method.name}
            </option>
          ))}
        </optgroup>
      ))}
    </select>
  );
};