import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import SummaryCard from '../components/SummaryCard';
import NetworkGraph from '../components/NetworkGraph';
import SuppliersView from '../components/SuppliersView';
import RiskOverview from '../components/RiskOverview';
import SettingsView from '../components/SettingsView';
import { summaryMetrics as defaultMetrics } from '../data/supplyChainData';
import { fetchGraphMetrics } from '../services/api';

export default function Dashboard({ activeTab, setIsSidebarOpen }) {
  const [metrics, setMetrics] = useState(defaultMetrics);

  useEffect(() => {
    async function loadMetrics() {
      const data = await fetchGraphMetrics();
      if (data) {
        setMetrics([
          {
            id: 'suppliers',
            title: 'Total Suppliers',
            value: String(data.total_suppliers),
            subtext: 'Tier 1 & Tier 2 verified partners',
            iconName: 'Building2',
          },
          {
            id: 'manufacturing',
            title: 'Manufacturing Units',
            value: String(data.manufacturing_units),
            subtext: 'Primary assembly & OEM plants',
            iconName: 'Factory',
          },
          {
            id: 'distribution',
            title: 'Logistics Hubs & Ports',
            value: String(data.distribution_centers),
            subtext: 'Maritime ports & regional DCs',
            iconName: 'Warehouse',
          },
          {
            id: 'disruptions',
            title: 'Active Disruptions',
            value: String(data.active_disruptions),
            subtext: `${data.high_risk_node_count} nodes in degraded state`,
            iconName: 'Store',
          },
        ]);
      }
    }
    loadMetrics();
  }, []);

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-slate-50 overflow-x-hidden">
      {/* Header */}
      <Header setIsOpen={setIsSidebarOpen} />

      {/* Main Content */}
      <main className="flex-1 p-6 max-w-7xl w-full mx-auto space-y-6">
        {/* Conditional Tab Views */}
        {activeTab === 'suppliers' && <SuppliersView />}
        {activeTab === 'risk' && <RiskOverview />}
        {activeTab === 'settings' && <SettingsView />}

        {/* Primary Dashboard & Network Flow Views */}
        {(activeTab === 'dashboard' || activeTab === 'network') && (
          <>
            {/* 4 Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {metrics.map((metric) => (
                <SummaryCard
                  key={metric.id}
                  title={metric.title}
                  value={metric.value}
                  subtext={metric.subtext}
                  iconName={metric.iconName}
                />
              ))}
            </div>

            {/* Main Network Graph */}
            <NetworkGraph />
          </>
        )}
      </main>
    </div>
  );
}
