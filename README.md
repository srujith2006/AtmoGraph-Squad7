# AtmoGraph – Backend Development

## 1. Project Overview

AtmoGraph is a graph-based global supply-chain analysis project designed to represent supply-chain entities, identify disruptions, and analyze relationships between different entities using Neo4j.

The backend is developed using Python and Neo4j AuraDB. It supports automated data ingestion, JSON validation, entity identification, relationship creation, and risk information management.

**Branch:** `Srujith-backend`

**Role:** Backend Developer

---

## 2. Technologies Used

- **Python** – Backend development and data processing
- **Neo4j AuraDB** – Graph database
- **Cypher** – Graph queries and relationship management
- **JSON** – Data exchange between NLP processing and backend
- **Git & GitHub** – Version control and collaboration

---

## 3. Project Structure

```text
AtmoGraph-Squad7/
│
├── backend/
│   ├── database/
│   │   ├── connection.py
│   │   ├── ingest.py
│   │   └── article_ingest.py
│   │
│   ├── data/
│   │   ├── mock_supply_chain.json
│   │   └── articles/
│   │       ├── sample_article.json
│   │       ├── sample_article_old.json
│   │       ├── test_no_ids.json
│   │       └── team_output.json
│   │
│   └── utils/
│       └── json_validator.py
│
├── .env.example
├── .gitignore
└── README.md
```

---

## 4. Week 1 – Graph Database Foundations

### 4.1 Neo4j Database Setup

- Configured Neo4j AuraDB.
- Established Python connectivity using the Neo4j Python driver.
- Configured database credentials using environment variables.
- Implemented connection verification.

### 4.2 Supply Chain Graph Design

Created the following entity types:

- Supplier
- Factory
- Port
- Warehouse
- Retailer

Implemented the following relationships:

- `SUPPLIES_TO`
- `SHIPS_TO`
- `TRANSPORTS_TO`
- `DISTRIBUTES_TO`

### 4.3 Automated Data Ingestion

Created a mock supply-chain dataset in JSON format and implemented Python scripts to automatically insert nodes and relationships into Neo4j.

**Week 1 Result:** Successfully created and populated the initial supply-chain graph.

---

## 5. Week 2 – GMRID JSON Integration and Backend Processing

### 5.1 Understanding the GMRID Dataset

- Studied the GMRID dataset structure and its article records.
- Identified the required fields for backend processing.
- Prepared a JSON structure containing article information, metadata, entities, relationships, and detected risks.
- Updated `sample_article.json` to follow the GMRID format.
- Preserved the previous sample JSON as `sample_article_old.json` for reference.

### 5.2 GMRID JSON Structure

The input JSON contains the following major fields:

| Field | Description |
|---|---|
| `record_id` | Unique article record identifier |
| `source` | Original dataset source |
| `article` | Complete article text |
| `metadata` | Dataset information and classification |
| `raw_fields` | Original dataset fields |
| `entities` | Extracted entities |
| `relationships` | Relationships between entities |
| `detected_risks` | Identified supply-chain risks |
| `severity_note` | Explanation of severity mapping |
| `risk_review_candidates_previous` | Previous risk review information |
| `detected_risks_initial` | Initial detected risk information |
| `risk_review_candidates` | Risks requiring review |

Metadata can contain:

- Date and region
- Latitude and longitude
- Found ports
- Port information availability
- Year, month, and week
- Original category
- Summarized label
- GPT-generated classification and specific tags
- Source severity

Optional metadata values can be `null`, and entity, relationship, and risk arrays can be empty.

### 5.3 JSON Validation

Updated `json_validator.py` to validate the GMRID JSON structure before database ingestion.

Validation includes:

- JSON syntax verification.
- Required field verification.
- Metadata structure and data-type validation.
- Entity type and ID validation.
- Duplicate entity ID and name checks.
- Relationship type validation.
- Entity reference verification.
- Detected risk validation.
- Risk severity validation.
- Risk review candidate validation.

Current entity types:

- `REGION`
- `LOCATION`
- `PORT`

Current relationship types include:

- `EXPERIENCING`
- `CAUSES`
- `LOCATED_IN`
- `AFFECTED_BY`

Supported risk severity levels:

- `LOW`
- `MEDIUM`
- `HIGH`

Supported risk review statuses:

- `CANDIDATE`
- `NEEDS_REVIEW`
- `CONTRADICTED`

### 5.4 Automatic Entity ID Generation

Implemented entity ID preparation in `article_ingest.py`.

- Existing entity IDs are preserved where available.
- Missing entity IDs are generated automatically.
- Deterministic UUID generation is used based on entity information.
- This allows the backend to process entities even when the input does not provide IDs.

### 5.5 Neo4j Article Ingestion

Updated `article_ingest.py` to process GMRID article records and store extracted information in Neo4j AuraDB.

The ingestion process:

1. Loads the GMRID JSON file.
2. Validates the input structure.
3. Prepares entity IDs.
4. Creates or updates Article nodes.
5. Stores article metadata.
6. Creates or updates entity nodes.
7. Creates Port nodes and preserves port mentions.
8. Connects articles to their entities.
9. Creates relationships between extracted entities when endpoints can be resolved.
10. Stores detected risk information.
11. Preserves risk review candidates separately.
12. Connects risks to locations when valid references are available.

### 5.6 Metadata Storage

Implemented article metadata storage in Neo4j.

- Stores complete metadata as a JSON string.
- Stores important metadata fields separately for easier querying.
- Preserves source severity independently from detected risk severity.
- Handles optional metadata values, including `null` values.
- Preserves original raw dataset information.

### 5.7 Transaction-Based Ingestion

Implemented Neo4j managed transactions using `session.execute_write()`.

This ensures that database operations for an article are executed within a managed transaction.

- Successful ingestion commits the changes.
- Failed operations can trigger transaction rollback.
- Helps prevent partially ingested article records.

### 5.8 GMRID Article Testing

Tested the updated backend using the GMRID sample article.

Test record:

- Record ID: `3390`
- Source: `GMRID_v3-test.csv`
- Region: India
- Port information: Chennai
- Detected risk: Port congestion
- Risk severity: HIGH

Successful terminal output confirmed:

- JSON syntax validation.
- GMRID record validation.
- Metadata validation.
- Entity validation.
- Relationship validation.
- Detected risk validation.
- Article creation in Neo4j.
- Port and entity connections.
- Risk-to-location relationship creation where resolvable.

**Week 2 Result:** Successfully validated and ingested a GMRID article record into Neo4j AuraDB.

---

## 6. Week 3 – Batch Ingestion and Knowledge Graph Visualization

### 6.1 Batch JSON Validation

Updated `json_validator.py` to support validation of multiple article records in a single JSON file.

Implemented:

- Batch JSON loading.
- Record-level validation.
- Required field verification.
- Metadata and raw field validation.
- Entity and relationship validation.
- Detected risk and review candidate validation.
- Validation error reporting.

Tested the validator using the complete Main Tech dataset.

**Validation Result:**

| Metric | Result |
|---|---:|
| Total records | 1,147 |
| Valid records | 1,147 |
| Invalid records | 0 |
| Validation errors | 0 |

### 6.2 Batch Article Ingestion

Reworked `article_ingest.py` to support batch processing of the Main Tech JSON output.

Implemented:

- Loading the complete JSON dataset.
- Validating all records before ingestion.
- Processing multiple article records.
- Creating Article nodes.
- Creating and connecting entity nodes.
- Processing detected risks.
- Preserving risk review candidates separately.
- Creating relationships when endpoints can be resolved.
- Reporting unresolved or ambiguous relationships.
- Tracking successful and failed records.
- Neo4j connection verification.
- Transaction-based processing for individual article records.

### 6.3 Main Tech Dataset Integration

Integrated the latest JSON output supplied by the Main Tech teammate.

The dataset contained 1,147 article records with extracted entities, relationships, metadata, and risk information.

The backend was adapted to process this batch structure without requiring individual article ingestion.

### 6.4 Batch Ingestion Testing

Executed:

```powershell
python backend/database/article_ingest.py
```

**Final Terminal Output:**

```text
========== INGESTION SUMMARY ==========

Total records: 1147
Successful records: 1147
Failed records: 0
Relationship/location warnings: 467

BATCH INGESTION COMPLETED.
```

**Final Results:**

| Metric | Result |
|---|---:|
| Total records | 1,147 |
| Successful records | 1,147 |
| Failed records | 0 |
| Relationship/location warnings | 467 |

All 1,147 records were processed successfully.

The warnings represent relationships or locations that could not be confidently resolved. They do not represent failed article records.

Further improvements to entity resolution and relationship accuracy are planned.

### 6.5 Neo4j Knowledge Graph Visualization

Verified the ingested graph using Neo4j AuraDB Query.

Used Cypher queries to visualize nodes and their relationships.

**Complete Graph Visualization:**

```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 200;
```

**Article-Related Graph:**

```cypher
MATCH (a:Article)-[r]->(n)
RETURN a, r, n
LIMIT 100;
```

**Detected Risk Connections:**

```cypher
MATCH (a:Article)-[r:HAS_DETECTED_RISK]->(risk)
RETURN a, r, risk
LIMIT 100;
```

**Graph Schema Visualization:**

```cypher
CALL db.schema.visualization();
```

These queries allow inspection of article nodes, entity connections, detected risks, and graph relationships directly in Neo4j.

**Week 3 Result:** Successfully validated and processed all 1,147 GMRID article records into Neo4j AuraDB with zero failed records. Verified the resulting knowledge graph through Neo4j visualization.

---

## 7. Current Backend Capabilities

| Feature | Status |
|---|---|
| Neo4j AuraDB connection | Completed |
| Supply-chain graph creation | Completed |
| Mock supply-chain data ingestion | Completed |
| GMRID JSON input support | Completed |
| JSON syntax validation | Completed |
| Batch JSON validation | Completed |
| Metadata validation | Completed |
| Entity validation | Completed |
| Relationship validation | Completed |
| Risk validation | Completed |
| Automatic entity ID generation | Implemented |
| Article node ingestion | Tested |
| Port and entity ingestion | Tested |
| Risk information ingestion | Tested |
| Article-to-entity connections | Tested |
| Transaction-based ingestion | Implemented |
| GMRID sample article integration | Tested |
| 1,147-record batch ingestion | Completed |
| Neo4j graph visualization | Verified |
| Entity resolution improvements | Planned |
| Dynamic JSON file discovery | Planned |
| Duplicate article detection | Planned |
| Live news/API integration | Planned |
| Backend API integration | Planned |

---

## 8. Running the Backend

### Step 1: Install Dependencies

```powershell
pip install neo4j python-dotenv certifi
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root using `.env.example` as a reference.

Configure:

```env
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
```

Do not commit the `.env` file to GitHub.

### Step 3: Configure SSL Certificate Path

For PowerShell:

```powershell
$env:SSL_CERT_FILE = python -c "import certifi; print(certifi.where())"
```

### Step 4: Validate the Complete Article Dataset

```powershell
python backend/utils/json_validator.py backend/data/articles/team_output.json
```

### Step 5: Run Batch Ingestion

```powershell
python backend/database/article_ingest.py
```

The default input file is:

`backend/data/articles/team_output.json`

### Step 6: Verify Data in Neo4j AuraDB

Connect to the database and execute:

```cypher
MATCH (n)
RETURN labels(n) AS NodeTypes, count(n) AS Total
ORDER BY Total DESC;
```

To inspect relationships:

```cypher
MATCH ()-[r]->()
RETURN type(r) AS RelationshipType, count(r) AS Total
ORDER BY Total DESC;
```

To visualize the graph schema:

```cypher
CALL db.schema.visualization();
```

---

## 9. Current Development Status

Week 1 focused on graph database foundations, including Neo4j AuraDB configuration, supply-chain graph design, and automated mock data ingestion.

Week 2 focused on GMRID JSON integration, article-level validation, entity processing, relationship creation, and detected risk management.

Week 3 focused on adapting the backend to the latest Main Tech batch JSON output. The validator successfully validated all 1,147 records, and the updated article ingestion pipeline processed all 1,147 records with zero failures. The resulting knowledge graph was also explored using Neo4j visualization queries.

The next development phase focuses on making the backend more dynamic, improving entity resolution accuracy, detecting duplicate articles, and supporting continuous knowledge graph updates.

---

## 10. Future Improvements

- Implement dynamic JSON file discovery and ingestion.
- Improve entity resolution using normalization and alias matching.
- Reduce unresolved and ambiguous relationship warnings.
- Implement duplicate article detection.
- Support continuous Neo4j graph updates.
- Introduce confidence-aware risk processing.
- Integrate live supply-chain news through reliable APIs.
- Integrate dynamically generated NLP outputs.
- Support prediction-related data in the graph.
- Develop backend APIs for frontend integration.
- Improve graph-based supply-chain risk analysis.

---

**AtmoGraph – Backend Development**

*Python | Neo4j AuraDB | Cypher | JSON | Knowledge Graphs*