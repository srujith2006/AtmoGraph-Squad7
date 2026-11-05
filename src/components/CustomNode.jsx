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
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
} from 'lucide-react';
import { nodeCategoryConfig } from '../data/supplyChainData';

const iconMap = {
  Boxes,
  Cpu,
  Factory,
  Truck,
  Store,
  Users,
};

function CustomNode({ data, selected }) {
  const config = nodeCategoryConfig[data.category] || nodeCategoryConfig.raw_material;
  const IconComponent = iconMap[config.icon] || Boxes;

  const isLowRisk = data.riskFactor?.toLowerCase().includes('low') || data.riskFactor?.toLowerCase().includes('minimal');

  return (
    <div
      className={`relative w-72 rounded-xl border-2 bg-white shadow-md transition-all duration-200 ${
        selected ? 'border-indigo-600 ring-4 ring-indigo-100 shadow-xl scale-[1.02]' : config.borderClass
      } hover:shadow-lg`}
    >
      {/* Input Handle (Left) */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-slate-600 !border-2 !border-white"
      />

      {/* Node Header Banner */}
      <div className={`flex items-center justify-between px-3.5 py-2 rounded-t-[10px] text-white ${config.headerBg}`}>
        <div className="flex items-center space-x-2">
          <div className="p-1 rounded bg-white/20 backdrop-blur-xs">
            <IconComponent className="w-4 h-4 text-white" />
          </div>
          <span className="text-xs font-semibold tracking-wide uppercase">{data.nodeType}</span>
        </div>
        <span className="text-[10px] font-medium bg-white/25 px-2 py-0.5 rounded-full">
          {config.badge}
        </span>
      </div>

      {/* Node Body */}
      <div className="p-3.5 space-y-2.5 bg-white">
        <div>
          <h4 className="text-sm font-bold text-slate-900 leading-snug line-clamp-1">
            {data.name}
          </h4>
          <p className="text-[11px] text-slate-500 font-medium">{data.tier}</p>
        </div>

        {/* Location & Output */}
        <div className="space-y-1 text-xs text-slate-600 pt-1 border-t border-slate-100">
          <div className="flex items-center space-x-1.5 text-slate-600">
            <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span className="truncate text-[11.5px]">{data.location}</span>
          </div>
          <div className="flex items-center space-x-1.5 text-slate-600">
            <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span className="text-[11.5px]">Lead Time: <strong className="text-slate-800">{data.leadTime}</strong></span>
          </div>
        </div>

        {/* Status Pill & Risk Badge */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-100">
          <div className="flex items-center space-x-1.5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-[11px] font-medium text-emerald-700">{data.status}</span>
          </div>

          <div
            className={`flex items-center space-x-1 px-2 py-0.5 rounded text-[10.5px] font-semibold ${
              isLowRisk ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
            }`}
          >
            {isLowRisk ? (
              <ShieldCheck className="w-3 h-3 text-emerald-600" />
            ) : (
              <AlertTriangle className="w-3 h-3 text-amber-600" />
            )}
            <span>{data.riskFactor}</span>
          </div>
        </div>
      </div>

      {/* Output Handle (Right) */}
      <Handle
        type="source"
        position={Position.Right}
        className="!w-3 !h-3 !bg-slate-600 !border-2 !border-white"
      />
    </div>
  );
}

export default memo(CustomNode);
