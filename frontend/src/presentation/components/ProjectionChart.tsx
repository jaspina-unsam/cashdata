/**
 * Component: ProjectionChart
 * 
 * Interactive chart showing 5-year savings projection with target cost overlay.
 * Uses Recharts for responsive visualization.
 */

import { AreaChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { MonthlyProjection } from '../../domain/entities';

interface ProjectionChartProps {
  data: MonthlyProjection[];
}

export function ProjectionChart({ data }: ProjectionChartProps) {
  // Format data for chart
  const chartData = data.map(m => ({
    month: m.month,
    label: m.date.toLocaleDateString('es-AR', { month: 'short', year: '2-digit' }),
    accumulated: Math.round(m.accumulatedSavings),
    target: Math.round(m.targetCost),
    income: Math.round(m.income),
  }));
  
  const formatCurrency = (value: number) => {
    return `$${(value / 1000).toFixed(0)}k`;
  };
  
  const formatTooltip = (value: number | undefined) => {
    if (value === undefined) return '';
    return `$${value.toLocaleString()}`;
  };
  
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
      <h3 className="text-lg font-bold text-slate-800 mb-4">
        📊 Evolución del plan (60 meses)
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorAhorro" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="label" 
            tick={{ fontSize: 11 }}
            interval={5}
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            tickFormatter={formatCurrency}
          />
          <Tooltip 
            formatter={formatTooltip}
            labelStyle={{ color: '#334155' }}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey="accumulated"
            stroke="#10b981"
            fillOpacity={1}
            fill="url(#colorAhorro)"
            name="Ahorro acumulado"
          />
          <Line 
            type="monotone" 
            dataKey="target" 
            stroke="#f97316" 
            strokeWidth={3}
            strokeDasharray="5 5"
            name="Costo de la obra"
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="income" 
            stroke="#8b5cf6" 
            strokeWidth={2}
            name="Ingreso mensual"
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
