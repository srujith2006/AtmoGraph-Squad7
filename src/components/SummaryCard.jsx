import React from 'react';
import { Building2, Factory, Warehouse, Store } from 'lucide-react';

const icons = {
  Building2,
  Factory,
  Warehouse,
  Store,
};

export default function SummaryCard({
  title,
  value,
  subtext,
  iconName = 'Building2',
}) {
  const Icon = icons[iconName] || Building2;

  return (
    <div className="bg-white rounded-xl p-5 border border-slate-200">
      <div className="flex items-center justify-between text-slate-500">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-500">
          {title}
        </span>
        <Icon className="w-4 h-4 text-slate-400" />
      </div>

      <div className="mt-2">
        <span className="text-2xl font-bold text-slate-900 tracking-tight">
          {value}
        </span>
      </div>

      <p className="mt-1 text-xs text-slate-400">
        {subtext}
      </p>
    </div>
  );
}
