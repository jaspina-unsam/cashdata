import React from 'react';
import type { PaymentMethod } from '../../domain';

interface PaymentMethodCardProps {
  paymentMethod: PaymentMethod;
  onClick?: () => void;
  variant?: 'default' | 'selected' | 'compact';
}

export const PaymentMethodCard: React.FC<PaymentMethodCardProps> = ({ paymentMethod, onClick, variant = 'default' }) => {
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

  const getVariantStyles = () => {
    switch (variant) {
      case 'selected':
        return 'bg-blue-50 border-blue-300 ring-2 ring-blue-200';
      case 'compact':
        return 'p-3 text-sm';
      default:
        return 'bg-white border-gray-200 hover:bg-gray-50';
    }
  };

  return (
    <div
      onClick={onClick}
      className={`
        border rounded-lg shadow-sm transition-all duration-200 cursor-pointer
        ${getVariantStyles()}
        ${variant === 'compact' ? 'p-3' : 'p-4'}
      `}
    >
      <div className="flex items-center space-x-3">
        <div className="text-2xl">
          {getIcon(paymentMethod.type)}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className={`font-medium text-gray-900 truncate ${variant === 'compact' ? 'text-sm' : 'text-base'}`}>
            {paymentMethod.name}
          </h3>
          <p className={`text-gray-500 capitalize ${variant === 'compact' ? 'text-xs' : 'text-sm'}`}>
            {paymentMethod.type.replace('_', ' ')}
          </p>
        </div>
        {variant === 'selected' && (
          <div className="text-blue-600">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
        )}
      </div>
    </div>
  );
}
