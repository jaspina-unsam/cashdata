/**
 * Component: ProjectionControls
 * 
 * Interactive controls for adjusting projection configuration.
 * Includes sliders for expenses, scenario selection, and economic factors.
 */

import type { ProjectionConfig } from '../../domain/entities';

interface ProjectionControlsProps {
  config: ProjectionConfig;
  onChange: (config: ProjectionConfig) => void;
  suggestedExpenses: { fixed: number; variable: number } | null;
}

export function ProjectionControls({ config, onChange, suggestedExpenses }: ProjectionControlsProps) {
  const handleChange = (field: keyof ProjectionConfig, value: any) => {
    onChange({ ...config, [field]: value });
  };
  
  const applyDetectedExpenses = () => {
    if (!suggestedExpenses) return;
    onChange({
      ...config,
      fixedExpenses: Math.round(suggestedExpenses.fixed),
      variableExpenses: Math.round(suggestedExpenses.variable),
    });
  };
  
  const scenarios = {
    conservative: { raise: 0, label: 'Sin aumento' },
    moderate: { raise: 10, label: 'Moderado (+10%/año)' },
    optimistic: { raise: 15, label: 'Optimista (+15%/año)' },
    very_optimistic: { raise: 25, label: 'Muy optimista (+25%/año)' },
  };
  
  const formatCurrency = (value: number) => `$${Math.round(value).toLocaleString()}`;
  
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Expenses Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-800">💰 Distribución mensual</h3>
            {suggestedExpenses && (
              <button
                onClick={applyDetectedExpenses}
                className="text-sm text-blue-600 hover:text-blue-800 underline"
              >
                Usar gastos detectados
              </button>
            )}
          </div>
          
          <div className="bg-red-50 p-4 rounded-lg border border-red-200">
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-semibold text-slate-700">
                🏠 Gastos Fijos
              </label>
              <span className="text-lg font-bold text-red-600">
                {formatCurrency(config.fixedExpenses)}
              </span>
            </div>
            <input
              type="range"
              min="500"
              max="1400"
              step="50"
              value={config.fixedExpenses}
              onChange={(e) => handleChange('fixedExpenses', Number(e.target.value))}
              className="w-full"
            />
            <div className="text-xs text-slate-600 mt-2">
              Expensas, servicios, comida, seguros
            </div>
          </div>
          
          <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-semibold text-slate-700">
                🛍️ Gastos Variables
              </label>
              <span className="text-lg font-bold text-orange-600">
                {formatCurrency(config.variableExpenses)}
              </span>
            </div>
            <input
              type="range"
              min="200"
              max="800"
              step="50"
              value={config.variableExpenses}
              onChange={(e) => handleChange('variableExpenses', Number(e.target.value))}
              className="w-full"
            />
            <div className="text-xs text-slate-600 mt-2">
              Entretenimiento, salidas, compras
            </div>
          </div>
          
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-semibold text-slate-700">
                🛡️ Fondo de Emergencia
              </label>
              <span className="text-lg font-bold text-blue-600">
                {formatCurrency(config.emergencyFundContribution)}
              </span>
            </div>
            <input
              type="range"
              min="50"
              max="300"
              step="25"
              value={config.emergencyFundContribution}
              onChange={(e) => handleChange('emergencyFundContribution', Number(e.target.value))}
              className="w-full"
            />
            <div className="text-xs text-slate-600 mt-2">
              Objetivo: USD 10,000
            </div>
          </div>
        </div>
        
        {/* Scenarios Section */}
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-slate-800">🚀 Escenarios</h3>
          
          <div className="bg-purple-50 p-4 rounded-lg border-2 border-purple-300">
            <label className="text-sm font-semibold text-slate-700 mb-2 block">
              📈 Proyección de carrera
            </label>
            <select
              value={config.professionalScenario}
              onChange={(e) => {
                const scenario = e.target.value as keyof typeof scenarios;
                handleChange('professionalScenario', scenario);
                handleChange('annualRaisePercentage', scenarios[scenario].raise);
              }}
              className="w-full p-2 rounded border border-purple-300 font-semibold"
            >
              {Object.entries(scenarios).map(([key, val]) => (
                <option key={key} value={key}>{val.label}</option>
              ))}
            </select>
          </div>
          
          <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-semibold text-slate-700">
                📉 Inflación construcción (% anual)
              </label>
              <span className="text-lg font-bold text-orange-600">
                {config.constructionInflationRate}%
              </span>
            </div>
            <input
              type="range"
              min="3"
              max="15"
              step="0.5"
              value={config.constructionInflationRate}
              onChange={(e) => handleChange('constructionInflationRate', Number(e.target.value))}
              className="w-full"
            />
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-semibold text-slate-700">
                🎯 Objetivo de ahorro
              </label>
              <span className="text-lg font-bold text-green-600">
                {formatCurrency(config.targetAmount)}
              </span>
            </div>
            <input
              type="range"
              min="50000"
              max="150000"
              step="5000"
              value={config.targetAmount}
              onChange={(e) => handleChange('targetAmount', Number(e.target.value))}
              className="w-full"
            />
          </div>
          
          <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-semibold text-slate-700">
                💹 Rendimiento inversión (% anual)
              </label>
              <span className="text-lg font-bold text-indigo-600">
                {config.investmentReturn}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="15"
              step="0.5"
              value={config.investmentReturn}
              onChange={(e) => handleChange('investmentReturn', Number(e.target.value))}
              className="w-full"
            />
            <div className="text-xs text-slate-600 mt-2">
              FCI, bonos, acciones
            </div>
          </div>
        </div>
        
      </div>
    </div>
  );
}
