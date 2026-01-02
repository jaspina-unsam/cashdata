/**
 * Credit Cards Page
 * 
 * Displays list of credit cards with ability to create new ones.
 */

import { useState } from 'react';
import { Plus, CreditCard as CreditCardIcon, User, Trash2 } from 'lucide-react';
import { useCreditCards, useCreateCreditCard, useUsers, useDeleteCreditCard } from '../../application';
import type { CreditCard } from '../../domain/entities';

// Default user ID for listing cards (will be replaced with auth context)
const DEFAULT_USER_ID = 1;

export function CreditCardsPage() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    user_id: '',
    name: '',
    bank: '',
    last_four_digits: '',
    billing_close_day: '',
    payment_due_day: '',
    credit_limit_amount: '',
    credit_limit_currency: 'ARS',
  });

  const { data: users } = useUsers();
  const { data: creditCards, isLoading, error } = useCreditCards(DEFAULT_USER_ID);
  const createCreditCard = useCreateCreditCard();
  const deleteCreditCard = useDeleteCreditCard();

  const handleDelete = async (cardId: number, cardName: string) => {
    if (!confirm(`¿Estás seguro que querés eliminar la tarjeta "${cardName}"? Esta acción no se puede deshacer.`)) {
      return;
    }

    try {
      await deleteCreditCard.mutateAsync({ id: cardId, userId: DEFAULT_USER_ID });
    } catch (err: any) {
      console.error('Failed to delete credit card:', err);
      alert(`Error al eliminar tarjeta: ${err.message || 'Error desconocido'}`);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.user_id || !formData.name.trim() || !formData.bank.trim() || 
        !formData.last_four_digits.trim() || !formData.billing_close_day || 
        !formData.payment_due_day) {
      alert('Por favor completá todos los campos obligatorios');
      return;
    }

    // Validate last 4 digits
    if (!/^\d{4}$/.test(formData.last_four_digits)) {
      alert('Los últimos 4 dígitos deben ser numéricos');
      return;
    }

    // Validate days
    const billingDay = parseInt(formData.billing_close_day);
    const paymentDay = parseInt(formData.payment_due_day);
    if (billingDay < 1 || billingDay > 31 || paymentDay < 1 || paymentDay > 31) {
      alert('Los días deben estar entre 1 y 31');
      return;
    }

    try {
      const cardData: Omit<CreditCard, 'id' | 'user_id'> = {
        name: formData.name.trim(),
        bank: formData.bank.trim(),
        last_four_digits: formData.last_four_digits,
        billing_close_day: billingDay,
        payment_due_day: paymentDay,
      };

      // Add credit limit if provided
      if (formData.credit_limit_amount) {
        cardData.credit_limit_amount = formData.credit_limit_amount;
        cardData.credit_limit_currency = formData.credit_limit_currency;
      }

      await createCreditCard.mutateAsync({ userId: parseInt(formData.user_id), data: cardData });
      
      // Reset form
      setFormData({
        user_id: '',
        name: '',
        bank: '',
        last_four_digits: '',
        billing_close_day: '',
        payment_due_day: '',
        credit_limit_amount: '',
        credit_limit_currency: 'ARS',
      });
      setShowForm(false);
    } catch (err: any) {
      console.error('Failed to create credit card:', err);
      alert(`Error al crear tarjeta: ${err.message || 'Error desconocido'}`);
    }
  };

  const handleCancel = () => {
    setFormData({
      user_id: '',
      name: '',
      bank: '',
      last_four_digits: '',
      billing_close_day: '',
      payment_due_day: '',
      credit_limit_amount: '',
      credit_limit_currency: 'ARS',
    });
    setShowForm(false);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Cargando tarjetas...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-600">Error al cargar tarjetas: {(error as Error).message}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Tarjetas de Crédito</h1>
              <p className="text-gray-600 mt-1">Gestioná tus tarjetas y seguí tus gastos</p>
            </div>
            <button
              onClick={() => setShowForm(!showForm)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <Plus size={20} />
              Nueva Tarjeta
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Create Form */}
        {showForm && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <h2 className="text-xl font-semibold mb-4">Nueva Tarjeta</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* User Selector */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <User className="inline w-4 h-4 mr-1" />
                    Titular *
                  </label>
                  <select
                    value={formData.user_id}
                    onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Seleccioná un titular</option>
                    {users?.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.name} ({user.email})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombre de la Tarjeta *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Ej: Visa Principal"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                {/* Bank */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Banco *
                  </label>
                  <input
                    type="text"
                    value={formData.bank}
                    onChange={(e) => setFormData({ ...formData, bank: e.target.value })}
                    placeholder="Ej: Santander"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                {/* Last 4 Digits */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Últimos 4 Dígitos *
                  </label>
                  <input
                    type="text"
                    value={formData.last_four_digits}
                    onChange={(e) => setFormData({ ...formData, last_four_digits: e.target.value })}
                    placeholder="1234"
                    maxLength={4}
                    pattern="\d{4}"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                {/* Billing Close Day */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Día de Cierre *
                  </label>
                  <input
                    type="number"
                    value={formData.billing_close_day}
                    onChange={(e) => setFormData({ ...formData, billing_close_day: e.target.value })}
                    placeholder="15"
                    min="1"
                    max="31"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                {/* Payment Due Day */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Día de Vencimiento *
                  </label>
                  <input
                    type="number"
                    value={formData.payment_due_day}
                    onChange={(e) => setFormData({ ...formData, payment_due_day: e.target.value })}
                    placeholder="10"
                    min="1"
                    max="31"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                {/* Credit Limit (Optional) */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Límite de Crédito (Opcional)
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      value={formData.credit_limit_amount}
                      onChange={(e) => setFormData({ ...formData, credit_limit_amount: e.target.value })}
                      placeholder="100000.00"
                      step="0.01"
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <select
                      value={formData.credit_limit_currency}
                      onChange={(e) => setFormData({ ...formData, credit_limit_currency: e.target.value })}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="ARS">ARS</option>
                      <option value="USD">USD</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 pt-4">
                <button
                  type="submit"
                  disabled={createCreditCard.isPending}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors disabled:opacity-50"
                >
                  {createCreditCard.isPending ? 'Creando...' : 'Crear Tarjeta'}
                </button>
                <button
                  type="button"
                  onClick={handleCancel}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-2 rounded-lg transition-colors"
                >
                  Cancelar
                </button>
              </div>

              {createCreditCard.isError && (
                <div className="mt-4 text-red-600">
                  Error: {(createCreditCard.error as Error).message}
                </div>
              )}
            </form>
          </div>
        )}

        {/* Credit Cards List */}
        {creditCards && creditCards.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {creditCards.map((card) => (
              <div
                key={card.id}
                className="bg-gradient-to-br from-blue-600 to-blue-800 text-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="p-2 bg-white/20 rounded-lg">
                    <CreditCardIcon size={24} />
                  </div>
                  <div className="text-right">
                    <p className="text-xs opacity-80">Día de cierre</p>
                    <p className="text-lg font-bold">{card.billing_close_day}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <h3 className="text-xl font-bold">{card.name}</h3>
                  <p className="text-blue-100">{card.bank}</p>
                  <p className="text-2xl font-mono tracking-wider">•••• {card.last_four_digits}</p>
                </div>

                <div className="mt-4 pt-4 border-t border-white/20 flex justify-between items-center">
                  <div>
                    <p className="text-xs opacity-80">Vencimiento</p>
                    <p className="font-semibold">Día {card.payment_due_day}</p>
                  </div>
                  {card.credit_limit_amount && (
                    <div className="text-right">
                      <p className="text-xs opacity-80">Límite</p>
                      <p className="font-semibold">
                        {card.credit_limit_currency} {parseFloat(card.credit_limit_amount).toLocaleString()}
                      </p>
                    </div>
                  )}
                </div>

                <div className="mt-4">
                  <button
                    onClick={() => handleDelete(card.id, card.name)}
                    disabled={deleteCreditCard.isPending}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors disabled:opacity-50"
                  >
                    <Trash2 size={16} />
                    {deleteCreditCard.isPending ? 'Eliminando...' : 'Eliminar'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white p-12 rounded-lg shadow-md text-center">
            <CreditCardIcon className="mx-auto text-gray-400 mb-4" size={48} />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No hay tarjetas</h3>
            <p className="text-gray-600 mb-4">Agregá tu primera tarjeta para comenzar a registrar gastos</p>
            <button
              onClick={() => setShowForm(true)}
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              <Plus size={20} />
              Nueva Tarjeta
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
