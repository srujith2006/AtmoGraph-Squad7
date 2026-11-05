import React from 'react';
import {
  LayoutDashboard,
  Network,
  Building2,
  AlertOctagon,
  Settings,
  Activity,
  Layers,
  Sparkles,
  ChevronRight,
  X,
} from 'lucide-react';

const navigationItems = [
  { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard },
  { id: 'network', name: 'Supply Chain Network', icon: Network, badge: 'Active' },
  { id: 'suppliers', name: 'Suppliers', icon: Building2, count: '24' },
  { id: 'risk', name: 'Risk Overview', icon: AlertOctagon, count: 'Low' },
  { id: 'settings', name: 'Settings', icon: Settings },
];

export default function Sidebar({ activeTab, setActiveTab, isOpen, setIsOpen }) {
  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-xs lg:hidden transition-opacity"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar Panel */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-72 bg-white border-r border-slate-200/90 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:z-auto ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 px-6 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-sky-400 flex items-center justify-center text-white shadow-md shadow-indigo-100">
              <Activity className="w-5 h-5 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <h1 className="font-extrabold text-lg text-slate-900 tracking-tight">
                  AtmoGraph
                </h1>
                <span className="text-[10px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-700 px-1.5 py-0.5 rounded border border-emerald-200/50">
                  Live
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium tracking-tight">
                Ripple Effect Predictor
              </p>
            </div>
          </div>

          {/* Close button for mobile view */}
          <button
            onClick={() => setIsOpen(false)}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 lg:hidden"
            aria-label="Close sidebar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Network Status Banner */}
        <div className="px-5 py-3">
          <div className="bg-gradient-to-r from-indigo-50/80 to-sky-50/80 border border-indigo-100/80 rounded-xl p-3">
            <div className="flex items-center space-x-2 text-indigo-700 font-semibold text-xs">
              <Activity className="w-4 h-4 text-indigo-500 shrink-0" />
              <span>Network Topology Active</span>
            </div>
            <p className="text-[11px] text-slate-600 mt-1 leading-relaxed">
              6 multi-tier echelons connected with end-to-end dependency tracking.
            </p>
          </div>
        </div>

        {/* Navigation Section */}
        <div className="flex-1 px-4 py-2 space-y-1 overflow-y-auto">
          <div className="px-3 pb-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            Navigation
          </div>
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id);
                  if (setIsOpen) setIsOpen(false);
                }}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-colors duration-150 group ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-200'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon
                    className={`w-4 h-4 transition-transform group-hover:scale-105 ${
                      isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-600'
                    }`}
                  />
                  <span>{item.name}</span>
                </div>

                <div className="flex items-center space-x-1.5">
                  {item.badge && (
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                        isActive
                          ? 'bg-white/20 text-white'
                          : 'bg-emerald-50 text-emerald-700 border border-emerald-200/60'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                  {item.count && (
                    <span
                      className={`text-xs px-2 py-0.5 rounded-md ${
                        isActive
                          ? 'bg-white/20 text-white'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {item.count}
                    </span>
                  )}
                  {isActive && <ChevronRight className="w-4 h-4 text-white/70" />}
                </div>
              </button>
            );
          })}
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/50">
          <div className="flex items-center space-x-3 p-2 rounded-xl bg-white border border-slate-200/80 shadow-xs">
            <div className="w-9 h-9 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-xs">
              SC
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-slate-800 truncate">Supply Chain Ops</p>
              <p className="text-[11px] text-slate-400 truncate">Global Operations Center</p>
            </div>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 ring-4 ring-emerald-100" />
          </div>
        </div>
      </aside>
    </>
  );
}
