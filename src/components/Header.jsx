import React, { useState, useEffect } from 'react';
import { Menu, Search, Bell, Activity } from 'lucide-react';
import { fetchHealth } from '../services/api';

export default function Header({ setIsOpen }) {
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    async function checkStatus() {
      const health = await fetchHealth();
      if (health && health.status === 'healthy') {
        setBackendStatus(`FastAPI v${health.version}`);
        setIsLive(true);
      } else {
        setBackendStatus('Offline (Mock Mode)');
        setIsLive(false);
      }
    }
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 px-6 bg-white border-b border-slate-200 flex items-center justify-between sticky top-0 z-30">
      {/* Left: Mobile Toggle & Page Title */}
      <div className="flex items-center space-x-3">
        <button
          onClick={() => setIsOpen(true)}
          className="p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 lg:hidden"
          aria-label="Open sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <h1 className="text-base font-semibold text-slate-900">
            AtmoGraph — Supply Chain Ripple Predictor
          </h1>
          <p className="text-xs text-slate-400 hidden sm:block">
            Real-time multi-hop graph disruption prediction
          </p>
        </div>
      </div>

      {/* Right: Search, Status, Profile */}
      <div className="flex items-center space-x-4">
        {/* Search */}
        <div className="relative hidden md:block w-64">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search nodes or facilities..."
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 text-slate-800 placeholder-slate-400"
          />
        </div>

        {/* Dynamic Backend Status Indicator */}
        <div
          className={`flex items-center space-x-1.5 text-xs px-2.5 py-1 rounded-full border font-medium ${
            isLive
              ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
              : 'text-amber-700 bg-amber-50 border-amber-200'
          }`}
        >
          <span
            className={`w-2 h-2 rounded-full ${
              isLive ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
            }`}
          />
          <span className="flex items-center gap-1">
            <Activity className="w-3 h-3" />
            {backendStatus}
          </span>
        </div>

        {/* Notifications */}
        <button
          className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-50"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}
