import React from 'react';
import { initialNodes } from '../data/supplyChainData';
import { Building2, MapPin, Clock, ShieldCheck, AlertTriangle, ExternalLink } from 'lucide-react';

export default function SuppliersView() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-5 rounded-xl border border-slate-200">
        <div>
          <h3 className="text-base font-bold text-slate-900">Supplier & Node Directory</h3>
          <p className="text-xs text-slate-500">
            Registered nodes across Tier 1, Tier 2, and internal manufacturing facilities
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            {initialNodes.length} Verified Facilities
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {initialNodes.map((node) => {
          const isLowRisk =
            node.data.riskFactor?.toLowerCase().includes('low') ||
            node.data.riskFactor?.toLowerCase().includes('minimal');

          return (
            <div
              key={node.id}
              className="bg-white rounded-xl p-5 border border-slate-200 hover:border-indigo-300 hover:shadow-md transition duration-150 flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <span className="text-[11px] font-bold text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full border border-indigo-100">
                    {node.data.nodeType}
                  </span>
                  <span
                    className={`inline-flex items-center space-x-1 text-[11px] font-semibold px-2 py-0.5 rounded ${
                      isLowRisk ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
                    }`}
                  >
                    {isLowRisk ? (
                      <ShieldCheck className="w-3 h-3 text-emerald-600" />
                    ) : (
                      <AlertTriangle className="w-3 h-3 text-amber-600" />
                    )}
                    <span>{node.data.riskFactor}</span>
                  </span>
                </div>

                <div>
                  <h4 className="text-sm font-bold text-slate-900">{node.data.name}</h4>
                  <p className="text-xs text-slate-500 font-medium">{node.data.tier}</p>
                </div>

                <div className="space-y-1.5 text-xs text-slate-600 pt-2 border-t border-slate-100">
                  <div className="flex items-center space-x-2">
                    <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span>{node.data.location}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span>Lead Time: <strong className="text-slate-800">{node.data.leadTime}</strong></span>
                  </div>
                </div>

                <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-100 text-xs">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">
                    Primary Output
                  </span>
                  <span className="text-slate-700 font-medium">{node.data.keyOutput}</span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="text-slate-400">Status: <strong className="text-emerald-600">{node.data.status}</strong></span>
                <span className="text-slate-400">Node ID: {node.id}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
