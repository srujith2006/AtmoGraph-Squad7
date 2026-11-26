/**
 * AtmoGraph API Integration Service
 * Connects React UI to FastAPI backend endpoints.
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function fetchHealth() {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('API health check unreachable:', err);
    return null;
  }
}

export async function fetchNeo4jHealth() {
  try {
    const res = await fetch(`${BASE_URL}/health/neo4j`);
    if (!res.ok) throw new Error(`Neo4j health check failed: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Neo4j health check unreachable:', err);
    return null;
  }
}

export async function fetchGraphTopology() {
  try {
    const res = await fetch(`${BASE_URL}/api/v1/graph/topology`);
    if (!res.ok) throw new Error(`Failed to fetch topology: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to fetch live topology from backend, using fallback:', err);
    return null;
  }
}

export async function fetchGraphMetrics() {
  try {
    const res = await fetch(`${BASE_URL}/api/v1/graph/metrics`);
    if (!res.ok) throw new Error(`Failed to fetch metrics: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Failed to fetch live metrics, using fallback:', err);
    return null;
  }
}

export async function simulateDisruption(targetNodeId, severity = 'High', description = 'Port strike & congestion delay', delayAddedDays = 14.0) {
  const res = await fetch(`${BASE_URL}/api/v1/graph/simulate-disruption`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      target_node_id: targetNodeId,
      new_risk_level: severity,
      disruption_description: description,
      delay_added_days: delayAddedDays,
    }),
  });
  if (!res.ok) throw new Error(`Disruption simulation failed: ${res.status}`);
  return await res.json();
}
