/**
 * Purchases Page
 * 
 * Displays list of purchases with ability to create new ones.
 */

import { useState } from 'react';
import { Plus, ShoppingCart, ChevronDown, ChevronUp, Trash2, Edit } from 'lucide-react';
import { usePurchases, useCreatePurchase, useDeletePurchase } from '../../application/hooks/usePurchases';
import { useCreditCards } from '../../application/hooks/useCreditCards';
import { useCategories } from '../../application/hooks/useCategories';
import type { Purchase } from '../../domain/entities';
import { useNavigate } from 'react-router-dom';
import DeletePurchaseModal from '../components/DeletePurchaseModal';

// Hardcoded user ID for MVP (will be replaced with auth context)
const CURRENT_USER_ID = 1;

// Helper function to format date string as local date (avoid timezone issues)
const formatLocalDate = (dateString: string): string => {
  const [year, month, day] = dateString.split('-').map(Number);
  const date = new Date(year, month - 1, day); // month is 0-indexed
  return date.toLocaleDateString('es-AR', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
};

export function PurchasesPage() {
  const [showForm, setShowForm] = useState(false);
  const [expandedPurchase, setExpandedPurchase] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    credit_card_id: '',
    category_id: '',
    purchase_date: new Date().toISOString().split('T')[0],
    description: '',
    total_amount: '',
    currency: 'ARS',
    installments_count: '1',
  });

  const { data: purchases, isLoading, error } = usePurchases(CURRENT_USER_ID);
  const { data: creditCards } = useCreditCards(CURRENT_USER_ID);
  const { data: categories } = useCategories();
  const createPurchase = useCreatePurchase();
  const deletePurchase = useDeletePurchase();

  const navigate = useNavigate();

  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ id: number; description?: string } | null>(null);

  const openDeleteModal = (id: number, description?: string) => {
    setDeleteTarget({ id, description });
    setDeleteModalOpen(true);
  };
  const closeDeleteModal = () => {
    setDeleteModalOpen(false);
    setDeleteTarget(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.credit_card_id || !formData.category_id || 
        !formData.description.trim() || !formData.total_amount) {
      alert('Por favor completá todos los campos obligatorios');
      return;
    }

    const installments = parseInt(formData.installments_count);
    if (installments < 1) {
      alert('Las cuotas deben ser al menos 1');
      return;
    }

    const amount = parseFloat(formData.total_amount);
    if (amount === 0) {
      alert('El monto no puede ser cero. Usá valores positivos para compras o negativos para créditos/bonificaciones.');
      return;
    }

    try {
      const purchaseData: Omit<Purchase, 'id' | 'user_id'> = {
        credit_card_id: parseInt(formData.credit_card_id),
        category_id: parseInt(formData.category_id),
        purchase_date: formData.purchase_date,
        description: formData.description.trim(),
        total_amount: parseFloat(formData.total_amount),
        currency: formData.currency,
        installments_count: installments,
      };

      await createPurchase.mutateAsync({ userId: CURRENT_USER_ID, data: purchaseData });
      
      // Reset form
      setFormData({
        credit_card_id: '',
        category_id: '',
        purchase_date: new Date().toISOString().split('T')[0],
        description: '',
        total_amount: '',
        currency: 'ARS',
        installments_count: '1',
      });
      setShowForm(false);
    } catch (err: any) {
      console.error('Failed to create purchase:', err);
      alert(`Error al crear compra: ${err.message || 'Error desconocido'}`);
    }
  };

  const handleCancel = () => {
    setFormData({
      credit_card_id: '',
      category_id: '',
      purchase_date: new Date().toISOString().split('T')[0],
      description: '',
      total_amount: '',
      currency: 'ARS',
      installments_count: '1',
    });
    setShowForm(false);
  };

  const togglePurchase = (purchaseId: number) => {
    setExpandedPurchase(expandedPurchase === purchaseId ? null : purchaseId);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Cargando compras...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-600">Error al cargar compras: {(error as Error).message}</div>
      </div>
    );
  }

  // Get card and category names for display
  const getCardName = (cardId: number) => {
    const card = creditCards?.find(c => c.id === cardId);
    return card ? `${card.name} •••• ${card.last_four_digits}` : 'Tarjeta desconocida';
  };

  const getCategoryName = (categoryId: number) => {
    const category = categories?.find(c => c.id === categoryId);
    return category?.name || 'Categoría desconocida';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Compras</h1>
              <p className="text-gray-600 mt-1">Registrá tus gastos y seguí tus cuotas</p>
            </div>
            <button
              onClick={() => setShowForm(!showForm)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <Plus size={20} />
              Nueva Compra
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Create Form */}
        {showForm && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <h2 className="text-xl font-semibold mb-4">Nueva Compra</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Credit Card */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tarjeta de Crédito *
                  </label>
                  <select
                    value={formData.credit_card_id}
                    onChange={(e) => setFormData({ ...formData, credit_card_id: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Seleccioná una tarjeta</option>
                    {creditCards?.map((card) => (
                      <option key={card.id} value={card.id}>
                        {card.name} - {card.bank} (•••• {card.last_four_digits})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Category */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Categoría *
                  </label>
                  <select
                    value={formData.category_id}
                    onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Seleccioná una categoría</option>
                    {categories?.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.icon} {category.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Purchase Date */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fecha de Compra *
                  </label>
                  <input
                    type="date"
                    value={formData.purchase_date}
                    onChange={(e) => setFormData({ ...formData, purchase_date: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Descripción *
                  </label>
                  <input
                    type="text"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Ej: Compra en supermercado"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                {/* Total Amount */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Monto Total * <span className="text-xs text-gray-500">(negativo para créditos)</span>
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      value={formData.total_amount}
                      onChange={(e) => setFormData({ ...formData, total_amount: e.target.value })}
                      placeholder="10000.00 (o -500.00 para crédito)"
                      step="0.01"
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    />
                    <select
                      value={formData.currency}
                      onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="ARS">ARS</option>
                      <option value="USD">USD</option>
                    </select>
                  </div>
                </div>

                {/* Installments Count */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Cantidad de Cuotas *
                  </label>
                  <input
                    type="number"
                    value={formData.installments_count}
                    onChange={(e) => setFormData({ ...formData, installments_count: e.target.value })}
                    placeholder="1"
                    min="1"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    1 = pago único, N = cuotas
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 pt-4">
                <button
                  type="submit"
                  disabled={createPurchase.isPending}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors disabled:opacity-50"
                >
                  {createPurchase.isPending ? 'Creando...' : 'Crear Compra'}
                </button>
                <button
                  type="button"
                  onClick={handleCancel}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-2 rounded-lg transition-colors"
                >
                  Cancelar
                </button>
              </div>

              {createPurchase.isError && (
                <div className="mt-4 text-red-600">
                  Error: {(createPurchase.error as Error).message}
                </div>
              )}
            </form>
          </div>
        )}

        {/* Purchases List */}
        {purchases && purchases.length > 0 ? (
          <div className="space-y-4">
            {purchases.map((purchase) => (
              <div
                key={purchase.id}
                className="bg-white rounded-lg shadow-md overflow-hidden"
              >
                {/* Purchase Header */}
                <div 
                  className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
                  onClick={() => togglePurchase(purchase.id!)}
                >
                  <div className="flex items-center gap-4 flex-1">
                    <div className="p-3 bg-blue-100 rounded-lg">
                      <ShoppingCart className="text-blue-600" size={24} />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900">{purchase.description}</h3>
                      <p className="text-sm text-gray-600">
                        {getCardName(purchase.credit_card_id)} • {getCategoryName(purchase.category_id)}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatLocalDate(purchase.purchase_date)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-gray-900">
                        {purchase.currency} {parseFloat(purchase.total_amount).toLocaleString()}
                      </p>
                      <p className="text-sm text-gray-600">
                        {purchase.installments_count === 1
                          ? 'Pago único'
                          : `${purchase.installments_count} cuotas`}
                      </p>

                      {/* Buttons placed bottom-right, visually-only (no action) */}
                      <div className="flex justify-end gap-3 mt-3">
                        <button
                          onClick={(e) => { e.stopPropagation(); openDeleteModal(purchase.id!, purchase.description); }}
                          className="flex items-center gap-1 text-red-600 hover:text-red-700 text-sm"
                          aria-label="Eliminar compra"
                        >
                          <Trash2 size={14} />
                          Eliminar
                        </button>

                        <button
                          onClick={(e) => { e.stopPropagation(); navigate(`/purchases/${purchase.id}/edit`); }}
                          className="flex items-center gap-1 text-blue-600 hover:text-blue-700 text-sm"
                          aria-label="Editar compra"
                        >
                          <Edit size={14} />
                          Editar
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="ml-4">
                    {expandedPurchase === purchase.id ? (
                      <ChevronUp className="text-gray-400" size={20} />
                    ) : (
                      <ChevronDown className="text-gray-400" size={20} />
                    )}
                  </div>
                </div>

                {/* Purchase Details (Expandable) */}
                {expandedPurchase === purchase.id && (
                  <div className="border-t border-gray-200 p-4 bg-gray-50">
                    <h4 className="font-semibold text-gray-900 mb-3">Detalle de Cuotas</h4>
                    <div className="space-y-2">
                      {purchase.installments_count === 1 ? (
                        <div className="bg-white p-3 rounded-lg">
                          <div className="flex justify-between items-center">
                            <span className="text-gray-700">Pago único</span>
                            <span className="font-semibold">
                              {purchase.currency} {parseFloat(purchase.total_amount).toLocaleString()}
                            </span>
                          </div>
                        </div>
                      ) : (
                        Array.from({ length: purchase.installments_count }, (_, i) => {
                          const installmentAmount = parseFloat(purchase.total_amount) / purchase.installments_count;
                          return (
                            <div key={i} className="bg-white p-3 rounded-lg">
                              <div className="flex justify-between items-center">
                                <span className="text-gray-700">
                                  Cuota {i + 1}/{purchase.installments_count}
                                </span>
                                <span className="font-semibold">
                                  {purchase.currency} {installmentAmount.toFixed(2)}
                                </span>
                              </div>
                            </div>
                          );
                        })
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white p-12 rounded-lg shadow-md text-center">
            <ShoppingCart className="mx-auto text-gray-400 mb-4" size={48} />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No hay compras</h3>
            <p className="text-gray-600 mb-4">Registrá tu primera compra para comenzar</p>
            <button
              onClick={() => setShowForm(true)}
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              <Plus size={20} />
              Nueva Compra
            </button>
          </div>
        )}
      </div>

      <DeletePurchaseModal
        purchaseId={deleteTarget?.id ?? null}
        isOpen={deleteModalOpen}
        onClose={() => { closeDeleteModal(); if (deleteTarget && expandedPurchase === deleteTarget.id) setExpandedPurchase(null); }}
        description={deleteTarget?.description}
        userId={CURRENT_USER_ID}
      />
    </div>
  );
}
