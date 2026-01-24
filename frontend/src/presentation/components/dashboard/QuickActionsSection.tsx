import React from 'react';
import { NewIncomeModal } from '../modals/NewIncomeModal';
import { QuickPurchaseModal } from '../modals/QuickPurchaseModal';

export const QuickActionsSection: React.FC = () => {
  const [incomeOpen, setIncomeOpen] = React.useState(false);
  const [purchaseOpen, setPurchaseOpen] = React.useState(false);

  return (
    <div className="bg-white p-6 rounded-lg shadow flex flex-col items-center justify-center">
      <h3 className="text-lg font-medium mb-4">Acciones Rápidas</h3>
      <div className="flex gap-3">
        <button
          className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
          onClick={() => setIncomeOpen(true)}
        >
          + Nuevo Ingreso
        </button>
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          onClick={() => setPurchaseOpen(true)}
        >
          + Nuevo Gasto
        </button>
      </div>

      <NewIncomeModal isOpen={incomeOpen} onClose={() => setIncomeOpen(false)} />
      <QuickPurchaseModal isOpen={purchaseOpen} onClose={() => setPurchaseOpen(false)} />
    </div>
  );
};
