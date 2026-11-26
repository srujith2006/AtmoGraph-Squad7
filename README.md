# AtmoGraph – Supply Chain Ripple Effect Predictor and Backend

> Frontend dashboard and backend development for supply-chain graph analysis.

## Project Overview

AtmoGraph is a graph-based global supply-chain analysis project. It combines a React dashboard for visualizing supply-chain networks and risks with a Python backend for data ingestion, validation, and Neo4j graph management.

## Frontend

The frontend is built with React 18, Vite, Tailwind CSS, React Flow, and Lucide icons. It includes dashboard, supplier, risk, settings, and network graph views.

### Run the frontend

```bash
npm install
npm run dev
```

## Backend

The backend uses Python, FastAPI, and Neo4j AuraDB for supply-chain graph operations, article ingestion, validation, and risk analysis.

### Run the backend

Install Python dependencies from `requirements.txt`, create a `.env` file using `.env.example`, and run the API with `python src/main.py`.

## Project Structure

```text
src/             Frontend and backend application code
docs/            API specification and OpenAPI schema
tests/           Backend tests
```

## Development Progress

The dashboard supports interactive supply-chain graph visualization and risk summaries. The backend supports JSON and batch article validation, entity and relationship processing, Neo4j ingestion, and FastAPI routes. The detailed backend development history from Weeks 1–3 follows.

---

## Backend Development History


