/**
 * Exchange Rates Page
 * 
 * Displays and manages exchange rates.
 */

import { useState } from 'react';
import { Plus, Trash2, TrendingUp, DollarSign } from 'lucide-react';
import { useExchangeRates, useCreateExchangeRate, useDeleteExchangeRate } from '../../application/hooks/useExchangeRates';
import type { ExchangeRateType, CreateExchangeRateData } from '../../domain/entities/ExchangeRate';
import { useActiveUser } from '../../application/contexts/UserContext';

const RATE_TYPE_LABELS: Record<ExchangeRateType, string> = {
  official: 'Oficial',
  blue: 'Blue',
  mep: 'MEP',
  ccl: 'CCL',
  custom: 'Custom',
  inferred: 'Inferido',
};

const RATE_TYPE_COLORS: Record<ExchangeRateType, string> = {
  official: 'bg-green-100 text-green-800',
  blue: 'bg-blue-100 text-blue-800',
  mep: 'bg-purple-100 text-purple-800',
  ccl: 'bg-pink-100 text-pink-800',
  custom: 'bg-orange-100 text-orange-800',
  inferred: 'bg-gray-100 text-gray-800',
};

export function ExchangeRatesPage() {
  const { activeUserId } = useActiveUser();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<CreateExchangeRateData>({
    date: new Date().toISOString().split('T')[0],
    from_currency: 'USD',
    to_currency: 'ARS',
    rate: 0,
    rate_type: 'official',
    source: '',
    notes: '',
  });

  const { data: exchangeRates, isLoading, error } = useExchangeRates(userId);
  const createExchangeRate = useCreateExchangeRate();
  const deleteExchangeRate = useDeleteExchangeRate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.rate <= 0) return;

    try {
      await createExchangeRate.mutateAsync({
        userId,
        data: {
          ...formData,
          source: formData.source || undefined,
          notes: formData.notes || undefined,
        },
      });
      setFormData({
        date: new Date().toISOString().split('T')[0],
        from_currency: 'USD',
        to_currency: 'ARS',
        rate: 0,
        rate_type: 'official',
        source: '',
        notes: '',
      });
      setShowForm(false);
    } catch (err) {
      console.error('Failed to create exchange rate:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('¿Estás seguro de eliminar este tipo de cambio?')) return;

    try {
      await deleteExchangeRate.mutateAsync({ id, userId });
    } catch (err) {
      console.error('Failed to delete exchange rate:', err);
    }
  };

  // Group rates by date
  const ratesByDate = exchangeRates?.reduce((acc, rate) => {
    if (!acc[rate.date]) {
      acc[rate.date] = [];
    }
    acc[rate.date].push(rate);
    return acc;
  }, {} as Record<string, typeof exchangeRates>);

  const sortedDates = Object.keys(ratesByDate || {}).sort().reverse();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Cargando tipos de cambio...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-600">Error al cargar tipos de cambio: {(error as Error).message}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <TrendingUp size={32} className="text-blue-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Tipos de Cambio</h1>
                <p className="text-gray-600 mt-1">Gestioná las cotizaciones USD/ARS</p>
              </div>
            </div>
            <button
              onClick={() => setShowForm(!showForm)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <Plus size={20} />
              Agregar Cotización
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Create Form */}
        {showForm && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <h2 className="text-xl font-semibold mb-4">Nueva Cotización</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fecha *
                  </label>
                  <input
                    type="date"
                    value={formData.date}
                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tipo *
                  </label>
                  <select
                    value={formData.rate_type}
                    onChange={(e) => setFormData({ ...formData, rate_type: e.target.value as ExchangeRateType })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="official">Oficial</option>
                    <option value="blue">Blue</option>
                    <option value="mep">MEP</option>
                    <option value="ccl">CCL</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Valor (ARS por USD) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.rate || ''}
                    onChange={(e) => setFormData({ ...formData, rate: parseFloat(e.target.value) || 0 })}
                    placeholder="1500.00"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notas (opcional)
                </label>
                <input
                  type="text"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Ej: Cotización del cierre del día"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={createExchangeRate.isPending || formData.rate <= 0}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors disabled:opacity-50"
                >
                  {createExchangeRate.isPending ? 'Guardando...' : 'Guardar'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-2 rounded-lg transition-colors"
                >
                  Cancelar
                </button>
              </div>
              {createExchangeRate.isError && (
                <div className="text-red-600">
                  Error: {(createExchangeRate.error as Error).message}
                </div>
              )}
            </form>
          </div>
        )}

        {/* Rates List */}
        {sortedDates.length === 0 ? (
          <div className="bg-white p-12 rounded-lg shadow-md text-center">
            <DollarSign size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 text-lg">No hay cotizaciones cargadas</p>
            <p className="text-gray-500 mt-2">Agregá tu primera cotización para comenzar</p>
          </div>
        ) : (
          <div className="space-y-6">
            {sortedDates.map((date) => (
              <div key={date} className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {new Date(date + 'T00:00:00').toLocaleDateString('es-AR', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </h3>
                </div>
                <div className="divide-y divide-gray-200">
                  {ratesByDate?.[date]?.map((rate) => (
                    <div
                      key={rate.id}
                      className="px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center gap-4 flex-1">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${RATE_TYPE_COLORS[rate.rate_type]}`}>
                          {RATE_TYPE_LABELS[rate.rate_type]}
                        </span>
                        <div className="flex items-center gap-2">
                          <span className="text-2xl font-bold text-gray-900">
                            ${rate.rate.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </span>
                          <span className="text-gray-500">ARS</span>
                        </div>
                        {rate.notes && (
                          <span className="text-gray-600 text-sm italic">- {rate.notes}</span>
                        )}
                      </div>
                      <button
                        onClick={() => handleDelete(rate.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Eliminar"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
