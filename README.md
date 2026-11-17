# AtmoGraph – Backend Development

## 1. Overview

This branch contains the backend implementation for **AtmoGraph**, a graph-based global supply-chain analysis project.

The backend uses Python and Neo4j AuraDB to build and manage a supply-chain knowledge graph. It supports automated data ingestion, NLP-extracted entity processing, relationship mapping and supply-chain risk identification.

**Branch:** `Srujith-backend`  
**Current Phase:** Week 2 – NLP Integration and Backend Development  
**Status:** Week 1 Completed | Week 2 In Progress

---

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| Neo4j AuraDB | Graph database |
| Cypher | Graph queries and database operations |
| Neo4j Python Driver | Python–Neo4j connectivity |
| python-dotenv | Environment variable management |
| JSON | Data storage and NLP output exchange |
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
- Established Python connectivity with Neo4j AuraDB.
- Retrieved and verified the database node count.

### 3.6 Automated Data Ingestion

Implemented `backend/database/ingest.py` to automate the insertion of supply-chain data into Neo4j.

The ingestion workflow:

1. Reads mock supply-chain data from a JSON file.
2. Processes Supplier, Factory, Port, Warehouse and Retailer records.
3. Uses Cypher `MERGE` to match or create nodes based on unique IDs.
4. Creates directed relationships between corresponding nodes.
5. Updates node and relationship properties.
6. Executes database operations within a write transaction.

### 3.7 Duplicate Prevention and Verification

- Used `MERGE` to avoid duplicate nodes and relationships during repeated ingestion.
- Tested the ingestion script multiple times.
- Identified and corrected an extra relationship caused by inconsistent relationship-type capitalization.
- Verified the final Week 1 dataset contains five nodes and four relationships.

**Week 1 database verification:**

| Database Element | Count |
|---|---:|
| Nodes | 5 |
| Relationships | 4 |

**Week 1 Backend Status: All planned deliverables completed.**

---

## 4. Week 2 – NLP Integration and Backend Development

Week 2 focuses on integrating NLP-extracted information into the existing Neo4j graph database.

The backend receives structured JSON output containing article text, extracted entities, relationships and detected supply-chain risks.

### 4.1 Neo4j Connection Improvements

**File:** `backend/database/connection.py`

Updated the database connection module with the following features:

- Loads Neo4j credentials from the project's root-level `.env` file.
- Validates required environment variables:
  - `NEO4J_URI`
  - `NEO4J_USERNAME`
  - `NEO4J_PASSWORD`
- Creates a Neo4j driver using the configured AuraDB URI.
- Verifies database connectivity using `driver.verify_connectivity()`.
- Retrieves and displays the total number of nodes in the database.
- Handles connection errors and closes the driver after testing.

**Connection test:**

```bash
python backend/database/connection.py
```

### 4.2 NLP JSON Input Structure

Defined and tested a JSON structure compatible with the NLP/NER extraction output.

The input contains the following major components:

| Field | Description |
|---|---|
| article | Original news article text |
| entities | Extracted entities with IDs, names and types |
| relationships | Relationships between extracted entities |
| detected_risks | Identified supply-chain risks |
| severity_note | Explanation of risk severity classification |

Supported entity types:

| NLP Entity Type | Neo4j Node Label |
|---|---|
| GPE | Location |
| RISK | Risk |
| SHIPMENT | Shipment |
| ORG | Organization |

### 4.3 JSON Validation

**File:** `backend/utils/json_validator.py`

Implemented a JSON validation script to check the incoming NLP article data.

The validator checks:

- Valid JSON syntax.
- Presence of required fields.
- Article text is provided as a string.
- Entities, relationships and detected risks are provided as lists.
- Required input structure is available before processing.

**Run the validator:**

```bash
python backend/utils/json_validator.py
```

### 4.4 NLP Article Ingestion into Neo4j

**File:** `backend/database/article_ingest.py`

Implemented an article ingestion module to process NLP-extracted information and store it in Neo4j.

The ingestion workflow includes:

1. Reads the sample NLP article JSON file.
2. Processes extracted entities.
3. Maps NLP entity types to corresponding Neo4j node labels.
4. Creates or matches entity nodes using Cypher `MERGE`.
5. Resolves entity names to their corresponding IDs.
6. Creates relationships between extracted entities.
7. Processes detected supply-chain risks.
8. Connects risks to relevant locations and affected entities.

### 4.5 Entity and Relationship Mapping

The backend converts NLP-extracted information into a graph representation.

Example entity relationships:

| Source Entity | Relationship | Target Entity |
|---|---|---|
| Port congestion | LOCATED_IN | Singapore |
| Port congestion | CAUSES | Shipment delay |
| Semiconductor shipments | AFFECTED_BY | Port congestion |
| Samsung | EXPERIENCING | Supply chain disruption |
| Intel | EXPERIENCING | Supply chain disruption |

Relationship evidence is stored as a property to retain supporting information from the source article.

### 4.6 Supply-Chain Risk Processing

The ingestion module processes detected risks and their associated information.

Risk properties include:

- Risk name
- Severity
- Evidence

The backend creates the following connections:

| Relationship | From | To |
|---|---|---|
| OCCURS_IN | Risk | Location |
| AFFECTS | Risk | Affected Entity |

This enables the graph to represent where a risk occurs and which supply-chain entities are affected.

### 4.7 Week 2 Testing and Verification

Tested the article ingestion workflow using `sample_article.json`.

**Sample entities processed:**

| Entity | Neo4j Label |
|---|---|
| Singapore | Location |
| Port congestion | Risk |
| Semiconductor shipments | Shipment |
| Shipment delay | Risk |
| Samsung | Organization |
| Intel | Organization |
| Supply chain disruption | Risk |

**Testing results:**

- Successfully processed seven extracted entities.
- Successfully created five NLP entity-to-entity relationships.
- Successfully processed three detected risks.
- Successfully connected risks to their locations and affected entities where provided.
- Verified the seven entity nodes and five NLP relationships in Neo4j Browser.
- Received the successful completion message: `Article ingestion completed successfully!`

**Note:** The seven entity nodes and five relationships refer to the sample NLP graph verification, not the total number of relationships in the database.

---

## 5. Project Structure

```text
AtmoGraph-Team7/
│
├── backend/
│   ├── database/
│   │   ├── connection.py
│   │   ├── ingest.py
│   │   └── article_ingest.py
│   │
│   ├── utils/
│   │   └── json_validator.py
│   │
│   ├── data/
│   │   ├── mock_supply_chain.json
│   │   └── articles/
│   │       └── sample_article.json
│   │
│   └── requirements.txt
│
├── .env.example
├── .gitignore
└── README.md
```

The actual `.env` file is stored locally and excluded from version control.

---

## 6. Backend Setup Instructions

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
NEO4J_URI=neo4j+s://your-aura-instance
NEO4J_USERNAME=your-username
NEO4J_PASSWORD=your-neo4j-password
```

Replace the placeholder values with your own Neo4j AuraDB credentials.

**Important:** Never commit or share the `.env` file.

### Step 4: Test database connectivity

```bash
python backend/database/connection.py
```

### Step 5: Run supply-chain data ingestion

```bash
python backend/database/ingest.py
```

### Step 6: Validate NLP JSON input

```bash
python backend/utils/json_validator.py
```

### Step 7: Run NLP article ingestion

```bash
python backend/database/article_ingest.py
```

The article ingestion module currently uses the sample article JSON file configured in the script.

---

## 7. Development Progress Tracker

### Week 1 – Graph Foundations

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

### Week 2 – NLP Integration and Backend Development

| Deliverable | Status |
|---|---|
| Neo4j connection improvements | Completed |
| NLP JSON structure design and sample preparation | Completed |
| JSON validator implementation | Completed |
| Entity-to-Neo4j label mapping | Completed |
| NLP entity ingestion | Completed |
| NLP relationship ingestion | Completed |
| Detected risk processing | Completed |
| Risk-to-location and risk-to-entity mapping | Completed |
| Sample article ingestion testing | Completed |
| Neo4j graph verification | Completed |
| Dynamic JSON file input | Pending |
| Automatic ID generation when IDs are missing | Pending |
| Stronger JSON and entity validation | Pending |
| Improved error handling and duplicate handling | Pending |
| Testing with actual NLP teammate output | Pending |
| Final Week 2 integration testing | Pending |

**Week 2 Backend Status: Core NLP article ingestion implemented and tested. Additional improvements and integration testing are in progress.**

---

## 8. Development Notes

- This README tracks backend-specific development.
- The main project README is maintained separately on the main branch.
- Database credentials must remain in local environment variables.
- Relationship types must follow consistent naming conventions.
- Cypher `MERGE` is used for matching or creating nodes and relationships.
- The backend is designed to consume structured JSON output from the NLP component.
- The backend implementation will be extended to support dynamic article inputs and flexible entity identification.

---

## 9. Upcoming Backend Work

The following tasks are planned to complete Week 2:

1. Implement dynamic JSON input so the ingestion module can process different article files.
2. Generate unique IDs automatically when the incoming JSON does not contain IDs.
3. Strengthen validation for entity types, names, relationship endpoints and risk severity.
4. Improve error handling for invalid or incomplete input.
5. Improve duplicate handling across multiple article ingestion runs.
6. Test the backend with actual JSON output from the NLP teammate.
7. Perform final Neo4j graph verification and update the project documentation.

---

**AtmoGraph – Backend Development**

*Week 1: Graph Foundations – Completed*  
*Week 2: NLP Integration and Backend Development – In Progress*