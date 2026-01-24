/**
 * Page: ProjectionsPage
 * 
 * Main page for 5-year financial projections.
 * Integrates all projection components and manages state.
 * 
 * Phase 1 (POC): Hardcoded to user_id = 1, ephemeral state.
 */

import { useState, useMemo, useEffect } from 'react';
import { useUserData, useLatestExchangeRate, calculateExpensesFromPurchases } from '../../application/hooks/useProjectionData';
import { projectionCalculator } from '../../application/services/projectionCalculator';
import { ProjectionControls } from '../components/ProjectionControls';
import { ProjectionChart } from '../components/ProjectionChart';
import { ProjectionSummary } from '../components/ProjectionSummary';
import { YearlySummaryTable } from '../components/YearlySummaryTable';
import { ProjectionRecommendations } from '../components/ProjectionRecommendations';
import type { ProjectionConfig } from '../../domain/entities';

const USER_ID = 1; // Hardcoded for Phase 1

export function ProjectionsPage() {
  const { user, purchases, isLoading: userLoading } = useUserData(USER_ID);
  const { data: latestRate, isLoading: rateLoading } = useLatestExchangeRate(USER_ID, 'blue');
  
  // Configuration state
  const [config, setConfig] = useState<ProjectionConfig>({
    userId: USER_ID,
    currentMonthlyIncome: 0, // Will be initialized from user data
    fixedExpenses: 900,
    variableExpenses: 400,
    emergencyFundContribution: 100,
    professionalScenario: 'moderate',
    annualRaisePercentage: 10,
    constructionInflationRate: 8,
    devaluationRate: 0,
    targetAmount: 75000,
    investmentReturn: 7,
  });
  
  // Initialize income from user data
  useEffect(() => {
    if (user && latestRate) {
      let incomeUSD = parseFloat(user.wage_amount);
      
      // Convert ARS to USD if needed
      if (user.wage_currency === 'ARS') {
        incomeUSD = incomeUSD / latestRate.rate;
      }
      
      setConfig((prev: ProjectionConfig) => ({ ...prev, currentMonthlyIncome: incomeUSD }));
    }
  }, [user, latestRate]);
  
  // Calculate detected expenses from purchases
  const detectedExpenses = useMemo(() => {
    if (!purchases.length || !latestRate) return null;
    return calculateExpensesFromPurchases(purchases, latestRate.rate);
  }, [purchases, latestRate]);
  
  // Calculate projection
  const projection = useMemo(() => {
    if (config.currentMonthlyIncome === 0) return null;
    return projectionCalculator.calculate({ config });
  }, [config]);
  
  if (userLoading || rateLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl text-slate-600">Cargando datos...</div>
      </div>
    );
  }
  
  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl text-red-600">Usuario no encontrado</div>
      </div>
    );
  }
  
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };
  
  return (
    <div className="max-w-7xl mx-auto p-6 bg-gradient-to-br from-slate-50 to-blue-50 min-h-screen">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <h1 className="text-3xl font-bold text-slate-800 mb-2">
          Plan de Ahorro Personalizado 2026-2030
        </h1>
        <div className="text-slate-600">
          <p className="text-sm">
            👤 Usuario: <strong>{user.name}</strong>
          </p>
          <p className="text-sm mt-1">
            💰 Ingreso actual: <strong className="text-blue-600">{formatCurrency(config.currentMonthlyIncome)}</strong>/mes
          </p>
          {detectedExpenses && (
            <div className="mt-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm text-blue-800 font-semibold">
                💡 Gastos detectados (últimos 6 meses):
              </p>
              <p className="text-sm text-blue-700 mt-1">
                🏠 Fijos: ~{formatCurrency(detectedExpenses.fixed)}/mes 
                {' | '}
                🛍️ Variables: ~{formatCurrency(detectedExpenses.variable)}/mes
                {' | '}
                📊 Total: {formatCurrency(detectedExpenses.total)}/mes
              </p>
              <p className="text-xs text-blue-600 mt-1">
                Usá el botón "Usar gastos detectados" en los controles para aplicarlos
              </p>
            </div>
          )}
          {!latestRate && (
            <div className="mt-2 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <p className="text-sm text-yellow-800">
                ⚠️ No se encontró tipo de cambio dólar blue. Las conversiones ARS→USD pueden no estar disponibles.
              </p>
            </div>
          )}
        </div>
      </div>
      
      {/* Controls */}
      <ProjectionControls
        config={config}
        onChange={setConfig}
        suggestedExpenses={detectedExpenses}
      />
      
      {/* Results */}
      {projection ? (
        <>
          <ProjectionSummary summary={projection.summary} />
          <ProjectionChart data={projection.months} />
          <YearlySummaryTable data={projection.months} />
          <ProjectionRecommendations recommendations={projection.recommendations} />
        </>
      ) : (
        <div className="bg-white rounded-xl shadow-lg p-6 text-center">
          <p className="text-slate-600">
            Configurando proyección...
          </p>
        </div>
      )}
      
      {/* Info Footer */}
      <div className="bg-white rounded-xl shadow-lg p-4 mt-6 text-center text-xs text-slate-500">
        <p>
          🔬 Fase 1 (POC) - Las proyecciones son estimativas y no persisten entre sesiones.
        </p>
        <p className="mt-1">
          Basado en tu ingreso actual, gastos históricos y escenarios económicos configurables.
        </p>
      </div>
    </div>
  );
}
