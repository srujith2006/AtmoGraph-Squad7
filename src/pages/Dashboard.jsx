import React from 'react';
import Header from '../components/Header';
import SummaryCard from '../components/SummaryCard';
import NetworkGraph from '../components/NetworkGraph';
import SuppliersView from '../components/SuppliersView';
import RiskOverview from '../components/RiskOverview';
import SettingsView from '../components/SettingsView';
import { summaryMetrics } from '../data/supplyChainData';
import {
  Sparkles,
  GitBranch,
  ShieldAlert,
  Clock,
  CheckCircle2,
  Activity,
  Layers,
} from 'lucide-react';

export default function Dashboard({ activeTab, setIsSidebarOpen }) {
  return (
    <div className="flex-1 flex flex-col min-h-screen bg-slate-50 overflow-x-hidden">
      {/* Top Header */}
      <Header setIsOpen={setIsSidebarOpen} />

      {/* Main Content Area */}
      <main className="flex-1 p-4 lg:p-8 max-w-7xl w-full mx-auto space-y-6">
        {/* Render Tab Views Conditionally */}
        {activeTab === 'suppliers' && <SuppliersView />}
        {activeTab === 'risk' && <RiskOverview />}
        {activeTab === 'settings' && <SettingsView />}

        {/* Dashboard or Network Tab View */}
        {(activeTab === 'dashboard' || activeTab === 'network') && (
          <>
            {/* Welcome & Context Banner (on Dashboard tab) */}
            {activeTab === 'dashboard' && (
              <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-2xl p-6 text-white shadow-lg relative overflow-hidden">
                <div className="absolute right-0 top-0 bottom-0 w-1/3 opacity-10 bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:16px_16px] pointer-events-none" />

                <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-1.5">
                    <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-full bg-white/10 text-indigo-200 text-xs font-semibold backdrop-blur-xs">
                      <Sparkles className="w-3.5 h-3.5 text-sky-400" />
                      <span>AtmoGraph Supply Chain Ripple Predictor • Week 1 Milestone</span>
                    </div>
                    <h2 className="text-xl lg:text-2xl font-bold tracking-tight">
                      Supply Chain Ripple Effect Dashboard
                    </h2>
                    <p className="text-slate-300 text-xs sm:text-sm max-w-2xl leading-relaxed">
                      Explore an interactive multi-echelon network topology. In upcoming sprints,
                      AtmoGraph will simulate failure ripples and predict disruption propagation across upstream and downstream tiers.
                    </p>
                  </div>

                  <div className="flex items-center space-x-3 shrink-0">
                    <div className="px-4 py-2.5 rounded-xl bg-white/10 backdrop-blur-md border border-white/10 text-center">
                      <div className="text-[11px] uppercase tracking-wider text-slate-300 font-medium">
                        Ripple Risk Score
                      </div>
                      <div className="text-xl font-extrabold text-emerald-400">
                        14 <span className="text-xs font-normal text-slate-300">/ 100</span>
                      </div>
                    </div>

                    <div className="px-4 py-2.5 rounded-xl bg-white/10 backdrop-blur-md border border-white/10 text-center">
                      <div className="text-[11px] uppercase tracking-wider text-slate-300 font-medium">
                        Connected Nodes
                      </div>
                      <div className="text-xl font-extrabold text-sky-400">6</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TASK 3: Sample Summary Cards Grid */}
            <section aria-labelledby="summary-metrics-title">
              <div className="flex items-center justify-between mb-3.5">
                <div>
                  <h3 id="summary-metrics-title" className="text-sm font-bold text-slate-900 tracking-tight">
                    Key Supply Chain Metrics
                  </h3>
                  <p className="text-xs text-slate-500">
                    Baseline capacity, logistics nodes, and fulfillment centers (Sample Data)
                  </p>
                </div>
                <span className="text-[11px] font-semibold text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-full border border-indigo-100">
                  Week 1 Mock Models
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {summaryMetrics.map((metric) => (
                  <SummaryCard
                    key={metric.id}
                    title={metric.title}
                    value={metric.value}
                    change={metric.change}
                    changeType={metric.changeType}
                    subtext={metric.subtext}
                    iconName={metric.iconName}
                    accentColor={metric.accentColor}
                  />
                ))}
              </div>
            </section>

            {/* TASK 2: Static Supply Chain Network Graph Canvas */}
            <section aria-labelledby="network-visualization-title" className="space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <h3 id="network-visualization-title" className="text-base font-bold text-slate-900">
                    Supply Chain Network Topology
                  </h3>
                  <p className="text-xs text-slate-500">
                    Directional flow from raw material extraction to final customer delivery. Nodes can be panned, zoomed, and dragged.
                  </p>
                </div>

                <div className="flex items-center space-x-2 text-xs text-slate-500">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-lg bg-white border border-slate-200 font-medium text-slate-700 shadow-2xs">
                    <GitBranch className="w-3.5 h-3.5 mr-1 text-indigo-600" />
                    6 Echelon Sequential Flow
                  </span>
                </div>
              </div>

              {/* Interactive React Flow Container */}
              <NetworkGraph />
            </section>

            {/* Supplementary Information Grid (Supply Chain Tiers & Upcoming Capabilities) */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Echelon Flow Summary */}
              <div className="lg:col-span-2 bg-white rounded-xl p-5 border border-slate-200/90 shadow-2xs space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">Echelon Flow Path & Stages</h4>
                    <p className="text-xs text-slate-500">Current active sequence modeled for AtmoGraph</p>
                  </div>
                  <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">
                    All Stages Verified
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                  <div className="p-3 rounded-lg border border-slate-100 bg-slate-50/60">
                    <div className="text-[11px] font-bold text-emerald-700">1. Raw Materials</div>
                    <div className="text-xs font-semibold text-slate-800 mt-0.5">Apex Mining Corp</div>
                    <div className="text-[11px] text-slate-500 mt-1">Lead: 21 Days • Ocean Cargo</div>
                  </div>

                  <div className="p-3 rounded-lg border border-slate-100 bg-slate-50/60">
                    <div className="text-[11px] font-bold text-sky-700">2. Components</div>
                    <div className="text-xs font-semibold text-slate-800 mt-0.5">Synapse Microtech</div>
                    <div className="text-[11px] text-slate-500 mt-1">Lead: 14 Days • Air Cargo</div>
                  </div>

                  <div className="p-3 rounded-lg border border-slate-100 bg-slate-50/60">
                    <div className="text-[11px] font-bold text-indigo-700">3. Assembly</div>
                    <div className="text-xs font-semibold text-slate-800 mt-0.5">Atmo MegaPlant 01</div>
                    <div className="text-[11px] text-slate-500 mt-1">Lead: 7 Days • Rail Transit</div>
                  </div>

                  <div className="p-3 rounded-lg border border-slate-100 bg-slate-50/60">
                    <div className="text-[11px] font-bold text-amber-700">4. Distribution</div>
                    <div className="text-xs font-semibold text-slate-800 mt-0.5">Central Logistics Hub</div>
                    <div className="text-[11px] text-slate-500 mt-1">Lead: 3 Days • Ground Fleet</div>
                  </div>

                  <div className="p-3 rounded-lg border border-slate-100 bg-slate-50/60">
                    <div className="text-[11px] font-bold text-rose-700">5. Retail</div>
                    <div className="text-xs font-semibold text-slate-800 mt-0.5">Metro Store Network</div>
                    <div className="text-[11px] text-slate-500 mt-1">Lead: 1 Day • Storefronts</div>
                  </div>

                  <div className="p-3 rounded-lg border border-slate-100 bg-slate-50/60">
                    <div className="text-[11px] font-bold text-purple-700">6. Customer</div>
                    <div className="text-xs font-semibold text-slate-800 mt-0.5">Global End Consumers</div>
                    <div className="text-[11px] text-slate-500 mt-1">Fulfilled Same Day</div>
                  </div>
                </div>
              </div>

              {/* Project Roadmap / Next Milestones */}
              <div className="bg-white rounded-xl p-5 border border-slate-200/90 shadow-2xs space-y-3.5">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <h4 className="text-sm font-bold text-slate-900">Project Development Plan</h4>
                  <span className="text-[10px] uppercase font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                    Roadmap
                  </span>
                </div>

                <div className="space-y-3 text-xs">
                  <div className="flex items-start space-x-2.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-slate-800">Week 1: Frontend Dashboard</p>
                      <p className="text-slate-500 text-[11px]">Static React Flow graph, Tailwind styling, summary cards.</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-2.5 opacity-70">
                    <Clock className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-slate-700">Week 2: Ripple Simulation UI</p>
                      <p className="text-slate-400 text-[11px]">Interactive disturbance triggering & cascade animations.</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-2.5 opacity-70">
                    <Clock className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-slate-700">Week 3: Neo4j Graph DB Sync</p>
                      <p className="text-slate-400 text-[11px]">Dynamic graph queries & multi-tier supplier relationship storage.</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-2.5 opacity-70">
                    <Clock className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-slate-700">Week 4: ML Ripple Predictor</p>
                      <p className="text-slate-400 text-[11px]">GNN model inferences for bottleneck and shockwave impact.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
