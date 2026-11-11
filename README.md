# AtmoGraph – Backend Development

## 1. Overview

This branch contains the backend implementation for **AtmoGraph**, a graph-based global supply-chain analysis project.

The backend establishes the Neo4j graph database, manages supply-chain entities and relationships, and provides automated data ingestion using Python.

**Branch:** `Srujith-Backend`  
**Current Phase:** Week 1 – Graph Foundations  
**Status:** Week 1 Backend Deliverables Completed

---

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| Neo4j AuraDB | Graph database |
| Cypher | Graph queries and database operations |
| Neo4j Python Driver | Python–Neo4j connectivity |
| python-dotenv | Environment variable management |
| JSON | Mock supply-chain data storage |
| Git & GitHub | Version control |

---

## 3. Week 1 – Graph Foundations

### 3.1 Neo4j Database Setup

- Created a Neo4j AuraDB Free instance named `AtmoGraph`.
- Configured cloud database connectivity.
- Successfully verified database connectivity using Python.

### 3.2 Supply-Chain Graph Data Model

Designed a mock global supply-chain network with five node types.

| Node Label | Example Entity | ID |
|---|---|---|
| Supplier | Chip Supplier | S001 |
| Factory | India Factory | F001 |
| Port | Chennai Port | P001 |
| Warehouse | Singapore Warehouse | W001 |
| Retailer | US Retailer | R001 |

### 3.3 Relationships

Implemented four directed relationships:

| Relationship | From | To |
|---|---|---|
| SUPPLIES_TO | Supplier | Factory |
| SHIPS_TO | Factory | Port |
| TRANSPORTS_TO | Port | Warehouse |
| DISTRIBUTES_TO | Warehouse | Retailer |

Relationship properties include `lead_time_days` and, where applicable, `capacity`.

### 3.4 Database Constraints

Created unique constraints for the `id` property of all five node labels:

- Supplier
- Factory
- Port
- Warehouse
- Retailer

These constraints help prevent duplicate entities.

### 3.5 Python–Neo4j Connectivity

- Installed the Neo4j Python Driver and python-dotenv.
- Configured database credentials using a root-level `.env` file.
- Implemented `backend/database/connection.py`.
- Successfully connected Python to Neo4j AuraDB.
- Retrieved and verified the database node count through Python.

### 3.6 Automated Data Ingestion

Implemented `backend/database/ingest.py` to automate the insertion of supply-chain data into Neo4j.

The ingestion workflow:

1. Reads mock supply-chain data from a JSON file.
2. Processes Supplier, Factory, Port, Warehouse and Retailer records.
3. Uses Cypher `MERGE` to match or create nodes based on unique IDs.
4. Creates directed relationships between the corresponding nodes.
5. Updates node and relationship properties.
6. Executes database operations within a write transaction.

### 3.7 Duplicate Prevention and Verification

- Used `MERGE` to avoid duplicate nodes and relationships during repeated ingestion.
- Tested the ingestion script multiple times.
- Identified and corrected an extra relationship caused by inconsistent relationship-type capitalization (`Supplies_To` versus `SUPPLIES_TO`).
- Verified the final database contains five nodes and four relationships.

**Final database verification:**

| Database Element | Count |
|---|---:|
| Nodes | 5 |
| Relationships | 4 |

---

## 4. Project Structure

```text
AtmoGraph-Team7/
│
├── backend/
│   ├── database/
│   │   ├── connection.py
│   │   └── ingest.py
│   │
│   ├── data/
│   │   └── mock_supply_chain.json
│   │
│   └── requirements.txt
│
├── .env.example
├── .gitignore
└── README.md
```

The actual `.env` file is stored locally and excluded from version control.

---

## 5. Backend Setup Instructions

### Prerequisites

- Python installed
- Neo4j AuraDB instance
- Git installed

### Step 1: Clone the repository

```bash
git clone <repository-url>
cd AtmoGraph-Team7
```

### Step 2: Install dependencies

```bash
pip install -r backend/requirements.txt
```

### Step 3: Configure environment variables

Create a `.env` file in the repository root:

```env
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

Replace the placeholder values with your own Neo4j AuraDB credentials.

**Important:** Never commit or share the `.env` file.

### Step 4: Test database connectivity

```bash
python backend/database/connection.py
```

### Step 5: Run automated data ingestion

```bash
python backend/database/ingest.py
```

The script reads the mock JSON dataset and inserts or updates the corresponding nodes and relationships in Neo4j.

---

## 6. Week 1 Progress Tracker

| Deliverable | Status |
|---|---|
| Neo4j AuraDB setup | Completed |
| Supply-chain graph schema design | Completed |
| Node creation | Completed |
| Relationship creation | Completed |
| Unique constraints | Completed |
| Python–Neo4j connectivity | Completed |
| Mock JSON dataset preparation | Completed |
| Automated data ingestion | Completed |
| Duplicate prevention testing | Completed |
| Database verification | Completed |

**Week 1 Backend Status: All planned deliverables completed.**

---

## 7. Development Notes

- This README tracks backend-specific development on the `Srujith-Backend` branch.
- The main project README is maintained separately on the main branch.
- Database credentials must remain in local environment variables.
- Relationship types must follow consistent naming conventions.
- The ingestion script uses `MERGE` to support repeated execution without creating duplicate records for the same node IDs and relationship endpoints/types.

---

## 8. Upcoming Backend Work

The next development phases will build on this database foundation and follow the project's subsequent weekly deliverables.

---

**AtmoGraph – Backend Development**  
*Week 1: Graph Foundations – Completed*