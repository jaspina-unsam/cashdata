/**
 * Component: ProjectionSummary
 * 
 * Summary card showing key metrics from the projection.
 * Highlights whether the goal is achieved with conditional styling.
 */

import React from 'react';
import type { ProjectionSummary } from '@/domain/entities';

interface ProjectionSummaryProps {
  summary: ProjectionSummary;
}

export function ProjectionSummary({ summary }: ProjectionSummaryProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };
  
  const achieves = summary.achievesGoal;
  
  return (
    <div className={`p-6 rounded-xl mb-6 ${achieves ? 'bg-green-50 border-2 border-green-300' : 'bg-yellow-50 border-2 border-yellow-300'}`}>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <div className="text-sm font-semibold text-slate-600 mb-1">
            Total acumulado (dic 2030)
          </div>
          <div className="text-2xl font-bold text-green-700">
            {formatCurrency(summary.totalSaved)}
          </div>
        </div>
        
        <div>
          <div className="text-sm font-semibold text-slate-600 mb-1">
            Costo proyectado obra
          </div>
          <div className="text-2xl font-bold text-orange-700">
            {formatCurrency(summary.finalTargetCost)}
          </div>
        </div>
        
        <div>
          <div className="text-sm font-semibold text-slate-600 mb-1">
            {achieves ? '✅ Excedente' : '⚡ Diferencia'}
          </div>
          <div className={`text-2xl font-bold ${achieves ? 'text-green-700' : 'text-yellow-700'}`}>
            {formatCurrency(Math.abs(summary.surplusOrDeficit))}
          </div>
        </div>
        
        <div>
          <div className="text-sm font-semibold text-slate-600 mb-1">
            Fondo emergencia
          </div>
          <div className="text-2xl font-bold text-blue-700">
            {formatCurrency(summary.finalEmergencyFund)}
          </div>
        </div>
      </div>
      
      <div className="mt-4 text-sm text-slate-700">
        {achieves ? (
          <span className="font-semibold">
            🎉 ¡Excelente! Llegarías al objetivo con margen de seguridad.
          </span>
        ) : (
          <span className="font-semibold">
            💪 Muy cerca del objetivo. Considerá hacer el proyecto en 2 etapas o aumentá ingresos.
          </span>
        )}
      </div>
    </div>
  );
}
