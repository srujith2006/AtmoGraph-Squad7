import React from 'react';
import {
  Building2,
  Factory,
  Warehouse,
  Store,
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react';

const iconMap = {
  Building2,
  Factory,
  Warehouse,
  Store,
};

const accentStyles = {
  emerald: {
    bg: 'bg-emerald-50 text-emerald-600',
    border: 'border-emerald-100',
    ring: 'hover:border-emerald-300',
  },
  blue: {
    bg: 'bg-sky-50 text-sky-600',
    border: 'border-sky-100',
    ring: 'hover:border-sky-300',
  },
  amber: {
    bg: 'bg-amber-50 text-amber-600',
    border: 'border-amber-100',
    ring: 'hover:border-amber-300',
  },
  rose: {
    bg: 'bg-rose-50 text-rose-600',
    border: 'border-rose-100',
    ring: 'hover:border-rose-300',
  },
};

export default function SummaryCard({
  title,
  value,
  change,
  changeType = 'positive',
  subtext,
  iconName = 'Building2',
  accentColor = 'blue',
}) {
  const IconComponent = iconMap[iconName] || Building2;
  const style = accentStyles[accentColor] || accentStyles.blue;

  return (
    <div
      className={`bg-white rounded-xl p-5 border border-slate-200/80 shadow-xs hover:shadow-md transition-all duration-200 ${style.ring}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            {title}
          </p>
          <div className="flex items-baseline space-x-2 mt-2">
            <h3 className="text-2xl lg:text-3xl font-extrabold text-slate-900 tracking-tight">
              {value}
            </h3>
            {change && (
              <span
                className={`inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full ${
                  changeType === 'positive'
                    ? 'bg-emerald-50 text-emerald-700'
                    : changeType === 'negative'
                    ? 'bg-rose-50 text-rose-700'
                    : 'bg-slate-100 text-slate-700'
                }`}
              >
                {changeType === 'positive' && <TrendingUp className="w-3 h-3 mr-1" />}
                {changeType === 'negative' && <TrendingDown className="w-3 h-3 mr-1" />}
                {changeType === 'neutral' && <Minus className="w-3 h-3 mr-1" />}
                {change}
              </span>
            )}
          </div>
        </div>

        <div className={`p-3 rounded-xl ${style.bg} ${style.border} border`}>
          <IconComponent className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span className="truncate">{subtext}</span>
        <span className="text-[11px] font-medium text-slate-400 bg-slate-50 px-1.5 py-0.5 rounded">
          Sample Data
        </span>
      </div>
    </div>
  );
}
