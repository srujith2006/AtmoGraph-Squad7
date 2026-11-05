import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import {
  Boxes,
  Cpu,
  Factory,
  Truck,
  Store,
  Users,
  MapPin,
  Clock,
} from 'lucide-react';

const icons = {
  raw_material: Boxes,
  component: Cpu,
  assembly: Factory,
  distribution: Truck,
  retail: Store,
  customer: Users,
};

const categoryColors = {
  raw_material: { bar: 'bg-emerald-500', badge: 'bg-emerald-50 text-emerald-700' },
  component: { bar: 'bg-sky-500', badge: 'bg-sky-50 text-sky-700' },
  assembly: { bar: 'bg-indigo-500', badge: 'bg-indigo-50 text-indigo-700' },
  distribution: { bar: 'bg-amber-500', badge: 'bg-amber-50 text-amber-700' },
  retail: { bar: 'bg-rose-500', badge: 'bg-rose-50 text-rose-700' },
  customer: { bar: 'bg-purple-500', badge: 'bg-purple-50 text-purple-700' },
};

function CustomNode({ data, selected }) {
  const Icon = icons[data.category] || Boxes;
  const colors = categoryColors[data.category] || categoryColors.raw_material;

  return (
    <div
      className={`relative w-60 rounded-xl bg-white border transition-all duration-150 shadow-xs overflow-hidden ${
        selected ? 'border-indigo-600 ring-2 ring-indigo-100 shadow-md' : 'border-slate-200 hover:border-slate-300'
      }`}
    >
      {/* Target Handle (Left) */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-2.5 !h-2.5 !bg-slate-400 !border-2 !border-white"
      />

      {/* Top Category Accent Line */}
      <div className={`h-1.5 w-full ${colors.bar}`} />

      {/* Content */}
      <div className="p-3.5 space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1.5">
            <Icon className="w-3.5 h-3.5 text-slate-500" />
            <span className="text-[11px] font-medium text-slate-500">{data.tier}</span>
          </div>
          <span className="flex items-center space-x-1 text-[11px] text-emerald-600 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span>{data.status}</span>
          </span>
        </div>

        <div>
          <h4 className="text-xs font-bold text-slate-900 leading-snug">
            {data.nodeType}
          </h4>
          <p className="text-[11px] text-slate-500 truncate mt-0.5">
            {data.name}
          </p>
        </div>

        <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
          <span className="truncate">{data.location.split(',')[0]}</span>
          <span className="font-medium text-slate-600 shrink-0">{data.leadTime}</span>
        </div>
      </div>

      {/* Source Handle (Right) */}
      <Handle
        type="source"
        position={Position.Right}
        className="!w-2.5 !h-2.5 !bg-slate-400 !border-2 !border-white"
      />
    </div>
  );
}

export default memo(CustomNode);
