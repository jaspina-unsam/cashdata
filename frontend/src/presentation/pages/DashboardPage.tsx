import React, { useState } from 'react';
import { MetricsSection } from '../components/dashboard/MetricsSection';
import { BudgetSection } from '../components/dashboard/BudgetSection';
import { UpcomingInstallmentsSection } from '../components/dashboard/UpcomingInstallmentsSection';
import { QuickActionsSection } from '../components/dashboard/QuickActionsSection';
import { AnalyticsSection } from '../components/dashboard/AnalyticsSection';

export const DashboardPage: React.FC = () => {
  const [installmentsMonths, setInstallmentsMonths] = useState<number>(6);
  const [analyticsMonths, setAnalyticsMonths] = useState<number>(6);

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-3xl font-bold text-gray-800">Dashboard Financiero</h1>
      <MetricsSection />

      {/* Upcoming installments: full width (minus sidebar) */}
      <div>
        <UpcomingInstallmentsSection months={installmentsMonths} onMonthsChange={setInstallmentsMonths} />
      </div>

      {/* Budget section below, occupying the same width as before (left column of a 2-col layout) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="lg:col-span-1">
          <BudgetSection />
        </div>
        <div className="lg:col-span-1">
          <QuickActionsSection />
        </div>
      </div>

      {/* Analytics */}
      <AnalyticsSection months={analyticsMonths} onMonthsChange={setAnalyticsMonths} />
    </div>
  );
};
