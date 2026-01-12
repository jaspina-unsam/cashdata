import React, { useState } from 'react';
import { X } from 'lucide-react';
import { useCreateCashAccount } from '../../application/hooks/useCashAccounts';
import { useUsers } from '../../application/hooks/useUsers';
import type { CashAccount } from '../../domain';

interface CreateCashAccountModalProps {
  userId: number;
  onClose: () => void;
}

export const CreateCashAccountModal: React.FC<CreateCashAccountModalProps> = ({
  userId,
  onClose,
}) => {
  const [formData, setFormData] = useState({
    owner_user_id: userId, // Usuario titular de la cuenta
    name: '',
    currency: 'ARS',
  });

  const { data: users } = useUsers();

  const createCashAccount = useCreateCashAccount();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      alert('Por favor ingresa un nombre para la cuenta');
      return;
    }

    try {
      const accountData: Omit<CashAccount, 'id' | 'payment_method_id' | 'user_id'> = {
        name: formData.name.trim(),
        currency: formData.currency,
      };

      // Usar el usuario titular seleccionado en lugar del userId prop
      await createCashAccount.mutateAsync({ userId: formData.owner_user_id, data: accountData });
      onClose();
    } catch (error: any) {
      console.error('Error creating cash account:', error);
      alert(`Error al crear cuenta de efectivo: ${error?.message || 'Error desconocido'}`);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-lg">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Nueva Cuenta de Efectivo</h3>
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
              Titular de la cuenta *
            </label>
            <select
              value={formData.owner_user_id}
              onChange={(e) => setFormData({ ...formData, owner_user_id: Number(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              required
            >
              {users?.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.name}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-500">
              Selecciona quién será el dueño de esta cuenta de efectivo
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre de la cuenta *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Ej: Efectivo Personal"
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
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
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
              disabled={createCashAccount.isPending}
              className="px-4 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createCashAccount.isPending ? 'Creando...' : 'Crear Cuenta'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
