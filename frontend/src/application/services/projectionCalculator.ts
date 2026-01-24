/**
 * Projection Calculator Service
 * 
 * Calculates 5-year (60-month) financial projections based on configuration.
 * Handles salary growth, inflation, investment returns, and bonuses.
 */

import type { ProjectionConfig, ProjectionResult, MonthlyProjection, ProjectionSummary } from '../../domain/entities';

interface CalculateProjectionParams {
  config: ProjectionConfig;
}

export class ProjectionCalculator {
  
  /**
   * Calculate complete 60-month projection
   */
  calculate(params: CalculateProjectionParams): ProjectionResult {
    const { config } = params;
    const months: MonthlyProjection[] = [];
    
    let currentIncome = config.currentMonthlyIncome;
    let currentFixedExpenses = config.fixedExpenses;
    let currentVariableExpenses = config.variableExpenses;
    let accumulatedSavings = 0;
    let accumulatedEmergencyFund = 0;
    
    // Calculate monthly rates from annual percentages
    const monthlyRaise = config.annualRaisePercentage / 100 / 12;
    const monthlyInflation = Math.pow(1 + config.constructionInflationRate / 100, 1/12) - 1;
    const monthlyReturn = Math.pow(1 + config.investmentReturn / 100, 1/12) - 1;
    const monthlyDevaluation = config.devaluationRate / 100 / 12;
    
    const startDate = new Date(2026, 0, 1); // January 2026
    
    for (let month = 1; month <= 60; month++) {
      // Calculate current date
      const currentDate = new Date(startDate);
      currentDate.setMonth(currentDate.getMonth() + month - 1);
      
      // Apply progressive salary increase
      if (month > 1) {
        currentIncome *= (1 + monthlyRaise);
      }
      
      // Apply devaluation to expenses (for future ARS support)
      if (month > 1 && config.devaluationRate > 0) {
        currentFixedExpenses *= (1 - monthlyDevaluation);
        currentVariableExpenses *= (1 - monthlyDevaluation);
      }
      
      // Calculate monthly savings
      const totalExpenses = currentFixedExpenses + currentVariableExpenses;
      const monthlySavings = Math.max(0, currentIncome - totalExpenses - config.emergencyFundContribution);
      
      // Aguinaldo (bonus every 6 months: June, December)
      const isBonus = month % 6 === 0;
      const bonus = isBonus ? currentIncome * 0.5 : 0;
      
      // Accumulate savings with investment returns
      accumulatedSavings = (accumulatedSavings + monthlySavings + bonus) * (1 + monthlyReturn);
      
      // Emergency fund (no returns, capped at 10k)
      if (accumulatedEmergencyFund < 10000) {
        accumulatedEmergencyFund += config.emergencyFundContribution;
      }
      
      // Target cost with inflation
      const targetCost = config.targetAmount * Math.pow(1 + monthlyInflation, month);
      
      months.push({
        month,
        date: currentDate,
        income: currentIncome,
        fixedExpenses: currentFixedExpenses,
        variableExpenses: currentVariableExpenses,
        monthlySavings,
        accumulatedSavings,
        accumulatedEmergencyFund: Math.min(accumulatedEmergencyFund, 10000),
        targetCost,
        difference: accumulatedSavings - targetCost,
        bonus,
      });
    }
    
    // Generate summary
    const lastMonth = months[months.length - 1];
    const summary: ProjectionSummary = {
      totalSaved: lastMonth.accumulatedSavings,
      finalTargetCost: lastMonth.targetCost,
      achievesGoal: lastMonth.accumulatedSavings >= lastMonth.targetCost,
      surplusOrDeficit: lastMonth.difference,
      finalEmergencyFund: lastMonth.accumulatedEmergencyFund,
      averageMonthlyIncome: months.reduce((sum, m) => sum + m.income, 0) / 60,
      averageMonthlySavings: months.reduce((sum, m) => sum + m.monthlySavings, 0) / 60,
    };
    
    // Generate recommendations
    const recommendations = this.generateRecommendations(config, summary);
    
    return { months, summary, recommendations };
  }
  
  /**
   * Generate personalized recommendations based on results
   */
  private generateRecommendations(
    config: ProjectionConfig, 
    summary: ProjectionSummary
  ): string[] {
    const recommendations: string[] = [];
    
    // Goal achievement
    if (!summary.achievesGoal) {
      const shortfall = Math.abs(summary.surplusOrDeficit);
      const percentageShort = (shortfall / summary.finalTargetCost) * 100;
      
      if (percentageShort < 20) {
        recommendations.push(
          '🏗️ Estás muy cerca del objetivo. Considerá realizar el proyecto en 2 etapas para reducir costo inicial'
        );
      } else {
        recommendations.push(
          '💪 Considerá aumentar tu ingreso mediante freelance, certificaciones o cambio de empleo'
        );
      }
      
      recommendations.push(
        '📉 Reducir gastos variables en USD 50-100/mes puede marcar una gran diferencia'
      );
    } else {
      const surplus = summary.surplusOrDeficit;
      const surplusPercentage = (surplus / summary.finalTargetCost) * 100;
      
      if (surplusPercentage > 30) {
        recommendations.push(
          '🎉 ¡Excelente! Alcanzás tu objetivo con margen amplio. Podés considerar un proyecto más ambicioso'
        );
      } else {
        recommendations.push(
          '✅ ¡Muy bien! Alcanzás tu objetivo con margen de seguridad'
        );
      }
    }
    
    // Emergency fund
    if (config.emergencyFundContribution < 150) {
      recommendations.push(
        '🛡️ Recomendamos aumentar fondo de emergencia a USD 150/mes mínimo para mayor tranquilidad'
      );
    }
    
    // Professional scenario
    if (config.professionalScenario === 'conservative') {
      recommendations.push(
        '📈 Con tu perfil en tech y trabajo remoto, un escenario "moderado" u "optimista" es más realista'
      );
    } else if (config.professionalScenario === 'very_optimistic') {
      recommendations.push(
        '🎯 Escenario muy optimista: asegurate de tener un plan concreto para lograr estos aumentos'
      );
    }
    
    // High expenses warning
    const expenseRatio = (config.fixedExpenses + config.variableExpenses) / config.currentMonthlyIncome;
    if (expenseRatio > 0.7) {
      recommendations.push(
        '⚠️ Tus gastos representan más del 70% de tu ingreso. Buscá oportunidades de reducción'
      );
    }
    
    // Investment return optimization
    if (config.investmentReturn < 5) {
      recommendations.push(
        '💰 Considerá opciones de inversión con mejor rendimiento (FCI, bonos, acciones) para acelerar el ahorro'
      );
    }
    
    return recommendations;
  }
}

// Singleton instance
export const projectionCalculator = new ProjectionCalculator();
