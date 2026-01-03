/**
 * Statement Detail Page
 * 
 * Shows the detail of a monthly statement including:
 * - Statement dates (billing close, payment due)
 * - Period range
 * - All purchases and installments in a table
 * - Form to edit statement dates
 */

import { useState } from 'react';
import { useParams, Link } from 'react-router';
import { useStatement, useUpdateStatementDates } from '../../application/hooks/useStatements';

export function StatementDetailPage() {
  const { id } = useParams<{ id: string }>();
  const statementId = parseInt(id || '0', 10);
  const [userId] = useState(1); // TODO: Get from auth context

  const { data: statement, isLoading, error } = useStatement(statementId, userId);
  const updateMutation = useUpdateStatementDates();

  const [isEditing, setIsEditing] = useState(false);
  const [billingCloseDate, setBillingCloseDate] = useState('');
  const [paymentDueDate, setPaymentDueDate] = useState('');

  // Initialize form when statement loads
  if (statement && !billingCloseDate) {
    setBillingCloseDate(statement.billing_close_date);
    setPaymentDueDate(statement.payment_due_date);
  }

  const formatDate = (dateStr: string) => {
    const [year, month, day] = dateStr.split('-');
    return `${day}/${month}/${year}`;
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  const handleSaveDates = async () => {
    if (!statement) return;

    try {
      await updateMutation.mutateAsync({
        statementId: statement.id,
        userId,
        data: {
          billing_close_date: billingCloseDate,
          payment_due_date: paymentDueDate,
        },
      });
      setIsEditing(false);
    } catch (err) {
      alert('Error al actualizar fechas: ' + (err as Error).message);
    }
  };

  const handleCancelEdit = () => {
    if (statement) {
      setBillingCloseDate(statement.billing_close_date);
      setPaymentDueDate(statement.payment_due_date);
    }
    setIsEditing(false);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg text-gray-600">Cargando resumen...</div>
      </div>
    );
  }

  if (error || !statement) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg text-red-600">
          Error al cargar resumen: {error ? (error as Error).message : 'No encontrado'}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <Link
          to="/statements"
          className="text-blue-600 hover:text-blue-800 mb-4 inline-flex items-center"
        >
          <svg
            className="w-5 h-5 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Volver a resumenes
        </Link>
        <h1 className="text-3xl font-bold text-gray-800">
          {statement.credit_card_name}
        </h1>
      </div>

      {/* Statement Info Card */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <h3 className="text-sm font-semibold text-gray-600 mb-2">
              Periodo del Resumen
            </h3>
            <p className="text-lg text-gray-800">
              {formatDate(statement.period_start_date)} - {formatDate(statement.period_end_date)}
            </p>
          </div>
        </div>

        {isEditing ? (
          <div className="border-t pt-4">
            <h3 className="text-sm font-semibold text-gray-600 mb-3">
              Editar Fechas
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fecha de Cierre
                </label>
                <input
                  type="date"
                  value={billingCloseDate}
                  onChange={(e) => setBillingCloseDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fecha de Vencimiento
                </label>
                <input
                  type="date"
                  value={paymentDueDate}
                  onChange={(e) => setPaymentDueDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleSaveDates}
                disabled={updateMutation.isPending}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
              >
                {updateMutation.isPending ? 'Guardando...' : 'Guardar'}
              </button>
              <button
                onClick={handleCancelEdit}
                disabled={updateMutation.isPending}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
              >
                Cancelar
              </button>
            </div>
          </div>
        ) : (
          <div className="border-t pt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Fecha de Cierre</p>
                <p className="text-lg font-semibold text-gray-800">
                  {formatDate(statement.billing_close_date)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Fecha de Vencimiento</p>
                <p className="text-lg font-semibold text-gray-800">
                  {formatDate(statement.payment_due_date)}
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsEditing(true)}
              className="mt-4 px-4 py-2 bg-gray-100 text-gray-800 rounded-md hover:bg-gray-200"
            >
              Editar Fechas
            </button>
          </div>
        )}
      </div>

      {/* Purchases Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800">
            Compras en este Periodo ({statement.purchases.length})
          </h2>
        </div>

        {statement.purchases.length === 0 ? (
          <div className="px-6 py-12 text-center text-gray-500">
            No hay compras en este periodo
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fecha
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Descripción
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Categoria
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cuotas
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Monto
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {statement.purchases.map((purchase, index) => (
                  <tr key={`${purchase.id}-${index}`} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(purchase.purchase_date)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {purchase.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {purchase.category_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {purchase.installment_number !== null
                        ? `${purchase.installment_number}/${purchase.installments}`
                        : purchase.installments === 1
                        ? '1 pago'
                        : `${purchase.installments} cuotas`}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-medium">
                      {formatCurrency(purchase.amount, purchase.currency)}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="bg-gray-50">
                <tr>
                  <td colSpan={4} className="px-6 py-4 text-right text-sm font-semibold text-gray-900">
                    Total a Pagar:
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-lg font-bold text-gray-900 text-right">
                    {formatCurrency(statement.total_amount, statement.currency)}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
