import React, { useState } from 'react';
import { X } from 'lucide-react';
import { useCreateBankAccount } from '../../application/hooks/useBankAccounts';
import { useUsers } from '../../application/hooks/useUsers';
import type { BankAccount } from '../../domain';

interface CreateBankAccountModalProps {
  userId: number;
  onClose: () => void;
}

export const CreateBankAccountModal: React.FC<CreateBankAccountModalProps> = ({
  userId,
  onClose,
}) => {
  const [formData, setFormData] = useState({
    primary_user_id: userId,
    secondary_user_id: '',
    name: '',
    bank: '',
    account_type: 'checking',
    last_four_digits: '',
    currency: 'ARS',
  });

  const createBankAccount = useCreateBankAccount();
  const { data: users } = useUsers();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim() || !formData.bank.trim() || !formData.last_four_digits) {
      alert('Por favor completa todos los campos obligatorios');
      return;
    }

    if (formData.last_four_digits.length !== 4 || !/^\d+$/.test(formData.last_four_digits)) {
      alert('Los últimos 4 dígitos deben ser exactamente 4 números');
      return;
    }

    try {
      const accountData: Omit<BankAccount, 'id' | 'payment_method_id'> = {
        primary_user_id: formData.primary_user_id,
        secondary_user_id: formData.secondary_user_id ? Number(formData.secondary_user_id) : null,
        name: formData.name.trim(),
        bank: formData.bank.trim(),
        account_type: formData.account_type,
        last_four_digits: formData.last_four_digits,
        currency: formData.currency,
      };

      await createBankAccount.mutateAsync({ userId, data: accountData });
      onClose();
    } catch (error: any) {
      console.error('Error creating bank account:', error);
      alert(`Error al crear cuenta bancaria: ${error?.message || 'Error desconocido'}`);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-lg max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Nueva Cuenta Bancaria</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Titular principal *
            </label>
            <select
              value={formData.primary_user_id}
              onChange={(e) => setFormData({ ...formData, primary_user_id: Number(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              {users?.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Segundo titular (opcional)
            </label>
            <select
              value={formData.secondary_user_id}
              onChange={(e) => setFormData({ ...formData, secondary_user_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Sin segundo titular</option>
              {users?.filter(user => user.id !== formData.primary_user_id).map((user) => (
                <option key={user.id} value={user.id}>
                  {user.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre de la cuenta *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Ej: Cuenta Corriente Personal"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Banco *
            </label>
            <input
              type="text"
              value={formData.bank}
              onChange={(e) => setFormData({ ...formData, bank: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Ej: Banco Nación"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de cuenta
            </label>
            <select
              value={formData.account_type}
              onChange={(e) => setFormData({ ...formData, account_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="checking">Cuenta Corriente</option>
              <option value="savings">Caja de Ahorro</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Últimos 4 dígitos *
            </label>
            <input
              type="text"
              value={formData.last_four_digits}
              onChange={(e) => setFormData({ ...formData, last_four_digits: e.target.value.replace(/\D/g, '').slice(0, 4) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="1234"
              maxLength={4}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Moneda
            </label>
            <select
              value={formData.currency}
              onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="ARS">ARS - Peso Argentino</option>
              <option value="USD">USD - Dólar Estadounidense</option>
              <option value="EUR">EUR - Euro</option>
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={createBankAccount.isPending}
              className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createBankAccount.isPending ? 'Creando...' : 'Crear Cuenta'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
