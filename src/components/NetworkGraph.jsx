import React, { useState, useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import CustomNode from './CustomNode';
import { initialNodes, initialEdges, nodeCategoryConfig } from '../data/supplyChainData';
import {
  Maximize2,
  Info,
  Shield,
  Activity,
  ArrowRight,
  Sparkles,
  Layers,
  MapPin,
  Clock,
  Gauge,
  Send,
  X,
} from 'lucide-react';

const nodeTypes = {
  supplyChainNode: CustomNode,
};

export default function NetworkGraph() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState(null);

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  const legendItems = useMemo(
    () => [
      { key: 'raw_material', label: 'Raw Materials', color: 'bg-emerald-500' },
      { key: 'component', label: 'Components', color: 'bg-sky-500' },
      { key: 'assembly', label: 'Assembly Factory', color: 'bg-indigo-500' },
      { key: 'distribution', label: 'Distribution Hub', color: 'bg-amber-500' },
      { key: 'retail', label: 'Retail Outlets', color: 'bg-rose-500' },
      { key: 'customer', label: 'End Consumer', color: 'bg-purple-500' },
    ],
    []
  );

  return (
    <div className="relative w-full h-[620px] bg-slate-50 rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
      {/* Network Canvas Header / Toolbar */}
      <div className="px-5 py-3.5 bg-white border-b border-slate-200 flex flex-wrap items-center justify-between gap-3 z-10">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-slate-900">
                Supply Chain Flow Topology
              </h3>
              <span className="px-2 py-0.5 text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full">
                6 Multi-Tier Nodes Active
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Interactive end-to-end network representation from Tier-2 suppliers to consumers
            </p>
          </div>
        </div>

        {/* Legend */}
        <div className="hidden xl:flex items-center gap-3 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-600">
          <span className="font-semibold text-slate-700 text-[11px] uppercase tracking-wider">
            Legend:
          </span>
          {legendItems.map((item) => (
            <div key={item.key} className="flex items-center space-x-1.5">
              <span className={`w-2.5 h-2.5 rounded-full ${item.color}`}></span>
              <span className="text-[11px] text-slate-600 font-medium">{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Main Flow Canvas */}
      <div className="relative flex-1 w-full h-full">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.3}
          maxZoom={1.5}
          attributionPosition="bottom-right"
        >
          <Background color="#cbd5e1" gap={20} size={1.2} variant={BackgroundVariant.Dots} />
          <Controls position="bottom-left" showInteractive={false} className="shadow-md rounded-lg" />
          <MiniMap
            position="bottom-right"
            nodeColor={(node) => {
              const cat = node.data?.category;
              switch (cat) {
                case 'raw_material':
                  return '#10b981';
                case 'component':
                  return '#0284c7';
                case 'assembly':
                  return '#6366f1';
                case 'distribution':
                  return '#f59e0b';
                case 'retail':
                  return '#f43f5e';
                case 'customer':
                  return '#a855f7';
                default:
                  return '#64748b';
              }
            }}
            maskColor="rgba(241, 245, 249, 0.7)"
            className="border border-slate-300 rounded-lg overflow-hidden shadow-sm"
          />
        </ReactFlow>

        {/* Floating Instruction Badge */}
        <div className="absolute top-4 left-4 z-10 pointer-events-none">
          <div className="bg-white/90 backdrop-blur-sm border border-slate-200 px-3 py-1.5 rounded-lg shadow-xs flex items-center space-x-2 text-xs text-slate-600">
            <Info className="w-4 h-4 text-indigo-500" />
            <span>Click any node to inspect node specifications & lead times</span>
          </div>
        </div>

        {/* Selected Node Details Drawer */}
        {selectedNode && (
          <div className="absolute top-4 right-4 z-20 w-80 bg-white/95 backdrop-blur-md rounded-xl border border-slate-200 shadow-xl p-4 animate-in fade-in slide-in-from-right-4 duration-150">
            <div className="flex items-start justify-between pb-3 border-b border-slate-100">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                  {selectedNode.data.nodeType}
                </span>
                <h4 className="text-sm font-bold text-slate-900 mt-1">
                  {selectedNode.data.name}
                </h4>
                <p className="text-xs text-slate-500">{selectedNode.data.tier}</p>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-md hover:bg-slate-100 transition"
                title="Close Inspector"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="mt-3 space-y-2.5 text-xs">
              <div className="flex items-center justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" /> Facility Location
                </span>
                <span className="font-semibold text-slate-800">{selectedNode.data.location}</span>
              </div>

              <div className="flex items-center justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-slate-400" /> Production Lead Time
                </span>
                <span className="font-semibold text-slate-800">{selectedNode.data.leadTime}</span>
              </div>

              <div className="flex items-center justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500 flex items-center gap-1.5">
                  <Gauge className="w-3.5 h-3.5 text-slate-400" /> Operating Capacity
                </span>
                <span className="font-semibold text-slate-800">{selectedNode.data.capacity}</span>
              </div>

              <div className="flex items-center justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500 flex items-center gap-1.5">
                  <Shield className="w-3.5 h-3.5 text-slate-400" /> Ripple Risk Score
                </span>
                <span className="font-semibold text-emerald-600">{selectedNode.data.riskFactor}</span>
              </div>

              <div className="flex items-center justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500 flex items-center gap-1.5">
                  <Send className="w-3.5 h-3.5 text-slate-400" /> Logistics Method
                </span>
                <span className="font-semibold text-slate-800">{selectedNode.data.transitMethod}</span>
              </div>

              <div className="pt-1">
                <span className="text-[11px] text-slate-400 uppercase font-semibold">Primary Output Goods</span>
                <p className="text-xs font-medium text-slate-700 mt-0.5 bg-slate-50 p-2 rounded border border-slate-100">
                  {selectedNode.data.keyOutput}
                </p>
              </div>
            </div>

            <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
              <span>Node ID: {selectedNode.id}</span>
              <span className="text-emerald-600 font-medium">Status: {selectedNode.data.status}</span>
            </div>
          </div>
        )}
      </div>

      {/* Footer Info Strip */}
      <div className="px-5 py-2.5 bg-white/80 border-t border-slate-200 flex flex-wrap items-center justify-between text-xs text-slate-500">
        <div className="flex items-center space-x-2">
          <Activity className="w-3.5 h-3.5 text-emerald-500" />
          <span>Flow Mode: <strong>Synchronous Downstream Propagation</strong></span>
        </div>
        <div className="flex items-center space-x-4">
          <span>Pan: <strong>Click & Drag</strong></span>
          <span>Zoom: <strong>Scroll Wheel</strong></span>
          <span className="text-indigo-600 font-medium">Real-Time Network Telemetry</span>
        </div>
      </div>
    </div>
  );
}
