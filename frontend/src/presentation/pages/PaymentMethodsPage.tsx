/**
 * Payment Methods Page
 *
 * Displays list of payment methods grouped by type with ability to create new ones.
 */

import React, { useState } from 'react';
import { Plus, CreditCard, DollarSign, Building2, Smartphone } from 'lucide-react';
import { usePaymentMethods } from '../../application/hooks/usePaymentMethods';
import { PaymentMethodCard } from '../components/PaymentMethodCard';
import { CreateCashAccountModal } from '../components/CreateCashAccountModal';
import { CreateBankAccountModal } from '../components/CreateBankAccountModal';
import { CreateDigitalWalletModal } from '../components/CreateDigitalWalletModal';
import type { PaymentMethod } from '../../domain';

import { useActiveUser } from '../../application/contexts/UserContext';

export function PaymentMethodsPage() {
  const [modalType, setModalType] = useState<'cash' | 'bank' | 'digital' | null>(null);

  const { activeUserId } = useActiveUser();
  const { data: paymentMethods, isLoading, error, refetch } = usePaymentMethods(activeUserId);

  const getIcon = (type: string) => {
    switch (type) {
      case 'credit_card':
        return <CreditCard className="w-6 h-6" />;
      case 'cash':
        return <DollarSign className="w-6 h-6" />;
      case 'bank_account':
        return <Building2 className="w-6 h-6" />;
      case 'digital_wallet':
        return <Smartphone className="w-6 h-6" />;
      default:
        return <CreditCard className="w-6 h-6" />;
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

  const groupedMethods = React.useMemo(() => {
    if (!paymentMethods) return {};

    return paymentMethods.reduce((groups, method) => {
      if (!groups[method.type]) {
        groups[method.type] = [];
      }
      groups[method.type].push(method);
      return groups;
    }, {} as Record<string, PaymentMethod[]>);
  }, [paymentMethods]);

  const handleModalClose = () => {
    setModalType(null);
    refetch(); // Refresh the list after creating a new payment method
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">Error al cargar métodos de pago</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Métodos de Pago</h1>
          <p className="text-gray-600 mt-2">Gestioná tus tarjetas, cuentas y billeteras</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setModalType('cash')}
            className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Cuenta de Efectivo
          </button>
          <button
            onClick={() => setModalType('bank')}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Cuenta Bancaria
          </button>
          <button
            onClick={() => setModalType('digital')}
            className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Billetera Digital
          </button>
        </div>
      </div>

      {Object.keys(groupedMethods).length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No tenés métodos de pago configurados</p>
          <p className="text-sm text-gray-400">Agregá tu primera cuenta para empezar a registrar gastos</p>
        </div>
      ) : (
        <div className="space-y-8">
          {Object.entries(groupedMethods).map(([type, methods]) => (
            <div key={type} className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="text-blue-600">
                  {getIcon(type)}
                </div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {getTypeLabel(type)} ({methods.length})
                </h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {methods.map((method) => (
                  <PaymentMethodCard
                    key={method.id}
                    paymentMethod={method}
                    variant="default"
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modals */}
      {modalType === 'cash' && (
        <CreateCashAccountModal
          userId={activeUserId}
          onClose={handleModalClose}
        />
      )}
      {modalType === 'bank' && (
        <CreateBankAccountModal
          userId={activeUserId}
          onClose={handleModalClose}
        />
      )}
      {modalType === 'digital' && (
        <CreateDigitalWalletModal
          userId={activeUserId}
          onClose={handleModalClose}
        />
      )}
    </div>
  );
}