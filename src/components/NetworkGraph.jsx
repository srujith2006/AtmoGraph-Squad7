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
import { initialNodes, initialEdges } from '../data/supplyChainData';
import { X, MapPin, Clock, Gauge, Shield, Send } from 'lucide-react';

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

  const legend = useMemo(
    () => [
      { label: 'Raw Material', color: 'bg-emerald-500' },
      { label: 'Component', color: 'bg-sky-500' },
      { label: 'Assembly', color: 'bg-indigo-500' },
      { label: 'Distribution', color: 'bg-amber-500' },
      { label: 'Retail', color: 'bg-rose-500' },
      { label: 'Customer', color: 'bg-purple-500' },
    ],
    []
  );

  return (
    <div className="relative w-full h-[580px] bg-white rounded-xl border border-slate-200 overflow-hidden flex flex-col">
      {/* Canvas Header */}
      <div className="px-5 py-3 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3 bg-white z-10">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">
            Supply Chain Topology
          </h2>
          <p className="text-xs text-slate-400">
            Interactive directional flow across tiers
          </p>
        </div>

        {/* Minimal Legend */}
        <div className="flex items-center gap-3 text-xs text-slate-600">
          {legend.map((item) => (
            <div key={item.label} className="flex items-center space-x-1.5">
              <span className={`w-2 h-2 rounded-full ${item.color}`} />
              <span className="text-[11px] text-slate-500">{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Main Flow Canvas */}
      <div className="relative flex-1 w-full h-full bg-slate-50/50">
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
          maxZoom={1.4}
        >
          <Background color="#cbd5e1" gap={20} size={1} variant={BackgroundVariant.Dots} />
          <Controls position="bottom-left" showInteractive={false} className="shadow-xs rounded-lg" />
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
            maskColor="rgba(248, 250, 252, 0.7)"
            className="border border-slate-200 rounded-lg overflow-hidden shadow-xs"
          />
        </ReactFlow>

        {/* Selected Node Details Card */}
        {selectedNode && (
          <div className="absolute top-4 right-4 z-20 w-72 bg-white rounded-xl border border-slate-200 shadow-lg p-4 animate-in fade-in duration-150">
            <div className="flex items-start justify-between pb-2 border-b border-slate-100">
              <div>
                <span className="text-[10px] font-semibold uppercase text-indigo-600">
                  {selectedNode.data.nodeType}
                </span>
                <h4 className="text-sm font-bold text-slate-900">
                  {selectedNode.data.name}
                </h4>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-md hover:bg-slate-50"
                aria-label="Close"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="mt-3 space-y-2 text-xs">
              <div className="flex items-center justify-between text-slate-600">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5" /> Location
                </span>
                <span className="font-medium text-slate-800">{selectedNode.data.location}</span>
              </div>

              <div className="flex items-center justify-between text-slate-600">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5" /> Lead Time
                </span>
                <span className="font-medium text-slate-800">{selectedNode.data.leadTime}</span>
              </div>

              <div className="flex items-center justify-between text-slate-600">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Gauge className="w-3.5 h-3.5" /> Capacity
                </span>
                <span className="font-medium text-slate-800">{selectedNode.data.capacity}</span>
              </div>

              <div className="flex items-center justify-between text-slate-600">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <Shield className="w-3.5 h-3.5" /> Risk Score
                </span>
                <span className="font-medium text-emerald-600">{selectedNode.data.riskFactor}</span>
              </div>

              <div className="pt-2 border-t border-slate-100">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Primary Output</span>
                <p className="text-xs text-slate-700 mt-0.5">{selectedNode.data.keyOutput}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
