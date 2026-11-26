import React from 'react';
import { initialNodes } from '../data/supplyChainData';
import {
  AlertOctagon,
  ShieldAlert,
  ShieldCheck,
  TrendingUp,
  Activity,
  Layers,
  Sparkles,
} from 'lucide-react';

export default function RiskOverview() {
  return (
    <div className="space-y-6">
      {/* Risk Banner */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-indigo-600 mb-1">
            <ShieldAlert className="w-4 h-4" />
            <span className="text-xs font-bold uppercase tracking-wider">Ripple Risk Index</span>
          </div>
          <h3 className="text-lg font-bold text-slate-900">Network Vulnerability Matrix</h3>
          <p className="text-xs text-slate-500 max-w-xl mt-1">
            AtmoGraph assesses tier dependencies and highlights critical supply nodes prone to cascading delays.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="px-5 py-3 rounded-xl bg-emerald-50 border border-emerald-200 text-center">
            <span className="text-[11px] font-semibold text-emerald-700 block">Overall Network Health</span>
            <span className="text-2xl font-extrabold text-emerald-600">89%</span>
          </div>
          <div className="px-5 py-3 rounded-xl bg-amber-50 border border-amber-200 text-center">
            <span className="text-[11px] font-semibold text-amber-700 block">Nodes Under Watch</span>
            <span className="text-2xl font-extrabold text-amber-600">1</span>
          </div>
        </div>
      </div>

      {/* Node Vulnerability Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <h4 className="text-sm font-bold text-slate-900">Tier-by-Tier Risk Scoring</h4>
          <span className="text-xs text-slate-400">Baseline Static Evaluation</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-100">
              <tr>
                <th className="px-4 py-3">Node Name & Type</th>
                <th className="px-4 py-3">Location</th>
                <th className="px-4 py-3">Capacity</th>
                <th className="px-4 py-3">Lead Time</th>
                <th className="px-4 py-3">Vulnerability Level</th>
                <th className="px-4 py-3">Cascade Potential</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {initialNodes.map((node) => {
                const isModerate = node.data.riskFactor?.includes('Moderate');
                return (
                  <tr key={node.id} className="hover:bg-slate-50/80 transition">
                    <td className="px-4 py-3">
                      <div className="font-bold text-slate-900">{node.data.name}</div>
                      <div className="text-[11px] text-slate-500">{node.data.nodeType}</div>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{node.data.location}</td>
                    <td className="px-4 py-3 text-slate-600">{node.data.capacity}</td>
                    <td className="px-4 py-3 text-slate-600">{node.data.leadTime}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full font-semibold ${
                          isModerate
                            ? 'bg-amber-50 text-amber-700 border border-amber-200'
                            : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        }`}
                      >
                        {isModerate ? (
                          <AlertOctagon className="w-3 h-3 text-amber-500 mr-1" />
                        ) : (
                          <ShieldCheck className="w-3 h-3 text-emerald-500 mr-1" />
                        )}
                        {node.data.riskFactor}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-slate-600 font-medium">
                        {isModerate ? 'Downstream Buffer Delay (+4 Days)' : 'Negligible Cascade Impact'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="p-4 bg-indigo-50/60 border border-indigo-100 rounded-xl flex items-center space-x-3 text-xs text-indigo-900">
        <Sparkles className="w-5 h-5 text-indigo-500 shrink-0" />
        <p>
          <strong>Ripple Effect Simulation Engine:</strong> Analyzes synthetic stress tests
          (e.g., port bottlenecks, manufacturing outages) and models wave propagation across dependent downstream nodes.
        </p>
      </div>
    </div>
  );
}
