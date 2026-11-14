# AtmoGraph – Supply Chain Ripple Effect Predictor

> **Sprint Milestone: Week 1 Frontend Development**  
> Role: Senior Frontend Developer & React Engineer

---

## 📌 Project Overview

**AtmoGraph** is a supply-chain intelligence dashboard designed to visualize multi-tier supply chain networks, predict ripple effects, and identify vulnerability bottlenecks. 

During **Week 1**, the foundation of the frontend dashboard has been completed with a clean, responsive enterprise architecture, interactive React Flow network topology visualization, and static mock data models.

---

## 🚀 Week 1 Completed Tasks

### Task 1: React Dashboard Setup
- [x] Initialized modern React application configured with Vite and Tailwind CSS.
- [x] Implemented responsive **Sidebar navigation** (`Dashboard`, `Supply Chain Network`, `Suppliers`, `Risk Overview`, `Settings`) with mobile drawer support.
- [x] Built a **Header** featuring branding, real-time health indicator (`Network Healthy`), search bar, quick action buttons, and user profile badge.
- [x] Created clean and responsive layout with Tailwind CSS typography and spacing.

### Task 2: Static Supply Chain Network Graph
- [x] Implemented interactive network topology canvas using `@xyflow/react` (React Flow).
- [x] Created 6 sample echelon nodes:
  1. **Raw Material Supplier** (Apex Mining & Minerals Corp)
  2. **Component Manufacturer** (Synapse Microtech Ltd)
  3. **Assembly Factory** (Atmo Integrated MegaPlant 01)
  4. **Distribution Warehouse** (Central Logistics Hub Alpha)
  5. **Retail Store** (Metro Flagship Outlets)
  6. **Customer** (End Consumers & Enterprise Buyers)
- [x] Configured **directional arrows** (`MarkerType.ArrowClosed`) and animated transit paths displaying transport methods.
- [x] Designed custom nodes (`CustomNode.jsx`) with distinct echelon colors, icons, capacity metrics, lead times, and risk indicators.
- [x] Added interactive node inspection drawer displaying node details upon selection.
- [x] Integrated navigation controls (`Controls`), grid background (`Background`), and `MiniMap`.

### Task 3: Dashboard Design
- [x] Modern, clean, enterprise dashboard aesthetic (light background with slate, indigo, emerald, sky, and amber accents).
- [x] Created sample summary metric cards:
  - **Total Suppliers** (24 Active • 18 Primary, 6 Secondary)
  - **Manufacturing Units** (8 Facilities • 94.2% Capacity)
  - **Distribution Centers** (12 Hubs • 99.1% On-time dispatch)
  - **Retail Locations** (185 Fronts • Direct & Partner)
- [x] Added Ripple Risk Score indicator (14/100) and roadmap milestone overview.

### Task 4: Clean Component-Based Architecture
```
src/
├── components/
│   ├── CustomNode.jsx       # Custom React Flow node with tier badges & handles
│   ├── Header.jsx           # Top navigation, status indicator & actions
│   ├── NetworkGraph.jsx     # React Flow canvas, controls, minimap, & inspector
│   ├── RiskOverview.jsx     # Tier vulnerability scoring view
│   ├── SettingsView.jsx     # Mock configuration & preferences
│   ├── Sidebar.jsx          # Collapsible navigation sidebar
│   ├── SummaryCard.jsx      # Reusable KPI metric card
│   └── SuppliersView.jsx    # Supplier and facility directory
├── data/
│   └── supplyChainData.js   # Mock nodes, directional edges, and KPI metrics
├── pages/
│   └── Dashboard.jsx        # Main dashboard screen composing components
├── App.jsx                  # Root application container & tab router
├── index.css                # Tailwind CSS base styles and scrollbar overrides
└── main.jsx                 # Application entry point
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Framework** | React 18 |
| **Bundler / Dev Server** | Vite 6 |
| **Styling** | Tailwind CSS 3.4 & PostCSS |
| **Graph Visualization** | `@xyflow/react` (React Flow 12) |
| **Iconography** | `lucide-react` |
| **Font** | Inter |

---

## 💻 Getting Started

### Prerequisites
- Node.js (v18 or higher recommended)
- npm or pnpm

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd AtmoGraph

# Install dependencies
npm install
```

### Running the Development Server

```bash
npm run dev
```
The application will launch at `http://localhost:3000`.

### Building for Production

```bash
npm run build
```
Generates optimized static assets in the `dist/` directory.

### Previewing the Production Build

```bash
npm run preview
```

---

## 🗺️ Project Roadmap

- **Week 1 (Current):** React dashboard setup, responsive UI, static React Flow supply chain graph with mock data models.

