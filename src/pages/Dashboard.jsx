import React from 'react';
import Header from '../components/Header';
import SummaryCard from '../components/SummaryCard';
import NetworkGraph from '../components/NetworkGraph';
import SuppliersView from '../components/SuppliersView';
import RiskOverview from '../components/RiskOverview';
import SettingsView from '../components/SettingsView';
import { summaryMetrics } from '../data/supplyChainData';

export default function Dashboard({ activeTab, setIsSidebarOpen }) {
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
              {summaryMetrics.map((metric) => (
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
