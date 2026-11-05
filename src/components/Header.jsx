import React from 'react';
import { Menu, Search, Bell } from 'lucide-react';

export default function Header({ setIsOpen }) {
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
            Supply Chain Network
          </h1>
          <p className="text-xs text-slate-400 hidden sm:block">
            Multi-tier flow and node status overview
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

        {/* Status indicator */}
        <div className="flex items-center space-x-1.5 text-xs text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-100 font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          <span>Operational</span>
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
