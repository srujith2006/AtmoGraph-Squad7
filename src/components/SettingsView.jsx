import React from 'react';
import { Settings, Sliders, Database, Bell, Shield, Laptop } from 'lucide-react';

export default function SettingsView() {
  return (
    <div className="space-y-6">
      <div className="bg-white p-5 rounded-xl border border-slate-200">
        <h3 className="text-base font-bold text-slate-900">Application Configuration</h3>
        <p className="text-xs text-slate-500">
          Frontend environment settings, visualization preferences, and mock datasource controls
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 space-y-4">
          <div className="flex items-center space-x-3 text-slate-800">
            <Database className="w-5 h-5 text-indigo-600" />
            <h4 className="text-sm font-bold">Data Source Configuration</h4>
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            In Week 1, AtmoGraph operates exclusively on static mock data as per requirements. Neo4j graph database integration and backend REST endpoints will be linked in Week 3.
          </p>
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <span className="font-medium text-slate-700">Active Pipeline</span>
              <span className="text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                Static Mock Data (Active)
              </span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100 opacity-60">
              <span className="font-medium text-slate-700">Neo4j Bolt URI</span>
              <span className="font-mono text-slate-500">bolt://localhost:7687 (Week 3)</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 space-y-4">
          <div className="flex items-center space-x-3 text-slate-800">
            <Sliders className="w-5 h-5 text-indigo-600" />
            <h4 className="text-sm font-bold">Network Canvas Preferences</h4>
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            Controls for the React Flow topology display, animations, and edge styling.
          </p>
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <span className="font-medium text-slate-700">Animated Directional Flow</span>
              <span className="text-indigo-600 font-semibold">Enabled</span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <span className="font-medium text-slate-700">Interactive MiniMap</span>
              <span className="text-indigo-600 font-semibold">Enabled</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
