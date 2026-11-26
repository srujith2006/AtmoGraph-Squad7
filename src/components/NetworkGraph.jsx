import React, { useState, useEffect, useCallback, useMemo } from 'react';
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
import { fetchGraphTopology, simulateDisruption } from '../services/api';
import { X, MapPin, Clock, Gauge, Shield, Zap, RefreshCw, Activity } from 'lucide-react';

const nodeTypes = {
  supplyChainNode: CustomNode,
};

export default function NetworkGraph() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState(null);
  const [isLiveApi, setIsLiveApi] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [simulating, setSimulating] = useState(false);

  // Load live graph topology from FastAPI backend
  const loadTopology = useCallback(async () => {
    setIsLoading(true);
    const data = await fetchGraphTopology();
    if (data && data.react_flow_nodes && data.react_flow_nodes.length > 0) {
      setNodes(data.react_flow_nodes);
      setEdges(data.react_flow_edges || []);
      setIsLiveApi(true);
    } else {
      // Fallback to static mock data
      setIsLiveApi(false);
    }
    setIsLoading(false);
  }, [setNodes, setEdges]);

  useEffect(() => {
    loadTopology();
  }, [loadTopology]);

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  // Trigger live disruption simulation
  const handleSimulateDisruption = async () => {
    if (!selectedNode) return;
    setSimulating(true);
    try {
      const updated = await simulateDisruption(
        selectedNode.id,
        'High',
        `Simulated port strike & delay at ${selectedNode.data.name}`,
        14.0
      );
      if (updated && updated.react_flow_nodes) {
        setNodes(updated.react_flow_nodes);
        setEdges(updated.react_flow_edges);
        // Update selected node state locally
        const updatedSelected = updated.react_flow_nodes.find((n) => n.id === selectedNode.id);
        if (updatedSelected) setSelectedNode(updatedSelected);
      }
    } catch (err) {
      console.error('Disruption simulation error:', err);
    } finally {
      setSimulating(false);
    }
  };

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
        <div className="flex items-center space-x-3">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-semibold text-slate-900">
                Supply Chain Topology
              </h2>
              {isLiveApi ? (
                <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                  <Activity className="w-3 h-3 text-emerald-600 animate-pulse" />
                  FastAPI Live
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded-full">
                  Local Mock
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400">
              Interactive multi-tier supply chain directional flow
            </p>
          </div>
        </div>

        {/* Minimal Legend & Action Buttons */}
        <div className="flex items-center gap-3 text-xs text-slate-600">
          <div className="hidden sm:flex items-center gap-3">
            {legend.map((item) => (
              <div key={item.label} className="flex items-center space-x-1.5">
                <span className={`w-2 h-2 rounded-full ${item.color}`} />
                <span className="text-[11px] text-slate-500">{item.label}</span>
              </div>
            ))}
          </div>

          {/* Reload / Refresh Button */}
          <button
            onClick={loadTopology}
            disabled={isLoading}
            className="flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-600 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg transition-colors"
            title="Refresh from FastAPI backend"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-indigo-600' : ''}`} />
            <span>Sync</span>
          </button>
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
                case 'supplier':
                  return '#10b981';
                case 'component':
                  return '#0284c7';
                case 'assembly':
                case 'manufacturer':
                  return '#6366f1';
                case 'distribution':
                case 'port':
                case 'warehouse':
                  return '#f59e0b';
                case 'retail':
                case 'retailer':
                  return '#f43f5e';
                default:
                  return '#64748b';
              }
            }}
            maskColor="rgba(248, 250, 252, 0.7)"
            className="border border-slate-200 rounded-lg overflow-hidden shadow-xs"
          />
        </ReactFlow>

        {/* Selected Node Details Card & Disruption Simulator */}
        {selectedNode && (
          <div className="absolute top-4 right-4 z-20 w-80 bg-white rounded-xl border border-slate-200 shadow-xl p-4 animate-in fade-in duration-150">
            <div className="flex items-start justify-between pb-2 border-b border-slate-100">
              <div>
                <span className="text-[10px] font-semibold uppercase text-indigo-600 tracking-wider">
                  {selectedNode.data.nodeType || 'Node Details'}
                </span>
                <h4 className="text-sm font-bold text-slate-900 leading-tight">
                  {selectedNode.data.name}
                </h4>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-md hover:bg-slate-50 transition-colors"
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
                  <Shield className="w-3.5 h-3.5" /> Risk Level
                </span>
                <span
                  className={`font-semibold px-2 py-0.5 rounded text-[11px] ${
                    selectedNode.data.riskFactor === 'High' || selectedNode.data.riskFactor === 'Critical'
                      ? 'bg-rose-50 text-rose-600 border border-rose-200'
                      : selectedNode.data.riskFactor === 'Medium'
                      ? 'bg-amber-50 text-amber-600 border border-amber-200'
                      : 'bg-emerald-50 text-emerald-600 border border-emerald-200'
                  }`}
                >
                  {selectedNode.data.riskFactor}
                </span>
              </div>

              <div className="pt-2 border-t border-slate-100">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Primary Output</span>
                <p className="text-xs text-slate-700 mt-0.5">{selectedNode.data.keyOutput || 'General Cargo'}</p>
              </div>

              {/* Interactive Ripple Simulation Trigger */}
              <div className="pt-3 border-t border-slate-100">
                <button
                  onClick={handleSimulateDisruption}
                  disabled={simulating}
                  className="w-full flex items-center justify-center gap-1.5 py-2 px-3 text-xs font-semibold text-white bg-rose-600 hover:bg-rose-700 active:bg-rose-800 rounded-lg shadow-xs transition-all disabled:opacity-50"
                >
                  <Zap className={`w-3.5 h-3.5 ${simulating ? 'animate-bounce' : ''}`} />
                  <span>{simulating ? 'Simulating Ripple Effect...' : '⚡ Trigger Disruption Ripple'}</span>
                </button>
                <p className="text-[10px] text-slate-400 text-center mt-1">
                  Propagates delays & highlights at-risk routes in red
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
