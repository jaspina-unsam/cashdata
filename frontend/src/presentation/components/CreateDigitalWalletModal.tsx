import React, { useState } from 'react';
import { X } from 'lucide-react';
import { useCreateDigitalWallet } from '../../application/hooks/useDigitalWallets';
import { useUsers } from '../../application/hooks/useUsers';
import type { DigitalWallet } from '../../domain';

interface CreateDigitalWalletModalProps {
  userId: number;
  onClose: () => void;
}

export const CreateDigitalWalletModal: React.FC<CreateDigitalWalletModalProps> = ({
  userId,
  onClose,
}) => {
  const [formData, setFormData] = useState({
    owner_user_id: userId, // Usuario titular de la billetera
    name: '',
    provider: '',
    currency: 'ARS',
  });

  const { data: users } = useUsers();

  const createDigitalWallet = useCreateDigitalWallet();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim() || !formData.provider.trim()) {
      alert('Por favor completa todos los campos obligatorios');
      return;
    }

    try {
      const walletData: Omit<DigitalWallet, 'id' | 'payment_method_id' | 'user_id'> = {
        name: formData.name.trim(),
        provider: formData.provider.trim(),
        currency: formData.currency,
        identifier: '', // Optional field, can be empty
      };

      // Usar el usuario titular seleccionado en lugar del userId prop
      await createDigitalWallet.mutateAsync({ userId: formData.owner_user_id, data: walletData });
      onClose();
    } catch (error: any) {
      console.error('Error creating digital wallet:', error);
      alert(`Error al crear billetera digital: ${error?.message || 'Error desconocido'}`);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-lg">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Nueva Billetera Digital</h3>
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
              Titular de la billetera *
            </label>
            <select
              value={formData.owner_user_id}
              onChange={(e) => setFormData({ ...formData, owner_user_id: Number(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              required
            >
              {users?.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.name}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-500">
              Selecciona quién será el dueño de esta billetera digital
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre de la billetera *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Ej: Mercado Pago Personal"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Proveedor *
            </label>
            <select
              value={formData.provider}
              onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              required
            >
              <option value="">Seleccionar proveedor</option>
              <option value="mercadopago">Mercado Pago</option>
              <option value="personalpay">Personal Pay</option>
              <option value="other">Otro</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Moneda
            </label>
            <select
              value={formData.currency}
              onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
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
              disabled={createDigitalWallet.isPending}
              className="px-4 py-2 rounded-lg bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createDigitalWallet.isPending ? 'Creando...' : 'Crear Billetera'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
