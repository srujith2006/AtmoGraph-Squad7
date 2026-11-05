import React from 'react';
import {
  Menu,
  Search,
  Bell,
  RefreshCw,
  Share2,
  Database,
  Radio,
  SlidersHorizontal,
} from 'lucide-react';

export default function Header({ setIsOpen, onResetView }) {
  return (
    <header className="h-16 px-4 lg:px-8 bg-white border-b border-slate-200/90 flex items-center justify-between sticky top-0 z-30 shadow-xs">
      {/* Left: Mobile Toggle & Page Context */}
      <div className="flex items-center space-x-3 lg:space-x-4">
        <button
          onClick={() => setIsOpen(true)}
          className="p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100 lg:hidden transition"
          aria-label="Open sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-base lg:text-lg font-bold text-slate-900 leading-tight">
              Supply Chain Network Overview
            </h2>
            <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse" />
              Network Healthy
            </span>
          </div>
          <p className="hidden sm:block text-xs text-slate-400">
            Real-time multi-echelon network topology visualization
          </p>
        </div>
      </div>

      {/* Middle: Search Box */}
      <div className="hidden md:flex items-center max-w-sm w-full mx-4">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search suppliers, facilities, nodes..."
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-800 placeholder-slate-400"
          />
        </div>
      </div>

      {/* Right: Actions & Status */}
      <div className="flex items-center space-x-2.5">
        <div className="hidden xl:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600">
          <Radio className="w-3.5 h-3.5 text-indigo-500" />
          <span>Pipeline: <strong className="text-slate-800">Tier 2 to Consumer</strong></span>
        </div>

        <button
          onClick={() => {
            if (onResetView) onResetView();
          }}
          className="flex items-center space-x-1.5 px-3 py-2 text-xs font-semibold text-slate-700 hover:text-indigo-600 bg-slate-50 hover:bg-indigo-50/60 rounded-xl border border-slate-200/80 transition"
          title="Reset View"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Refresh Data</span>
        </button>

        <div className="relative">
          <button
            className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-xl transition"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-indigo-600 ring-2 ring-white" />
          </button>
        </div>

        <div className="h-6 w-px bg-slate-200 hidden sm:block" />

        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-sky-400 text-white flex items-center justify-center font-bold text-xs ring-2 ring-slate-100">
            AG
          </div>
          <div className="hidden md:block text-left">
            <p className="text-xs font-semibold text-slate-800 leading-none">Dev Team</p>
            <p className="text-[10px] text-slate-400 mt-0.5">AtmoGraph v0.1</p>
          </div>
        </div>
      </div>
    </header>
  );
}
