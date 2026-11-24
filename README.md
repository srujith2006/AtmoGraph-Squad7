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
AtmoGraph-Team7/
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
- Updated `sample_article.json` to follow the new GMRID format.
- Preserved the previous sample JSON as `sample_article_old.json` for reference.

The backend currently accepts the new GMRID JSON structure.

### 5.2 GMRID JSON Structure

The input JSON contains the following major fields:

| Field | Description |
|---|---|
| `record_id` | Unique article record identifier |
| `source` | Original dataset source |
| `article` | Complete article text |
| `metadata` | Dataset information and classification |
| `entities` | Extracted entities |
| `relationships` | Relationships between entities |
| `detected_risks` | Identified supply-chain risks |
| `severity_note` | Explanation of severity mapping |

The metadata can contain:

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

Updated `json_validator.py` to validate the new GMRID JSON format before database ingestion.

Validation includes:

- JSON syntax verification.
- Required top-level field verification.
- Metadata structure and data-type validation.
- Entity type and ID validation.
- Duplicate entity ID and name checks.
- Relationship type validation.
- Entity reference verification.
- Detected risk validation.
- Risk severity validation.
- Location and affected entity reference checks.

Supported entity types:

- `GPE`
- `RISK`
- `SHIPMENT`
- `ORG`

Supported relationship types:

- `LOCATED_IN`
- `CAUSES`
- `OCCURS_IN`
- `AFFECTS`
- `AFFECTED_BY`
- `EXPERIENCING`

Supported risk severity levels:

- `LOW`
- `MEDIUM`
- `HIGH`

### 5.4 Automatic Entity ID Generation

Implemented entity ID preparation in `article_ingest.py`.

- Existing entity IDs are preserved.
- Missing entity IDs are generated automatically.
- Deterministic UUID generation is used based on entity type and name.
- This allows the backend to process entities even when the input does not provide IDs.

### 5.5 Neo4j Article Ingestion

Updated `article_ingest.py` to process GMRID article records and store the extracted information in Neo4j AuraDB.

The ingestion process:

1. Loads the GMRID JSON file.
2. Validates the input structure.
3. Prepares entity IDs.
4. Creates or updates the Article node.
5. Stores article metadata.
6. Creates or updates Port nodes.
7. Creates entity nodes.
8. Connects articles to their entities.
9. Creates relationships between extracted entities.
10. Updates detected risk information.
11. Connects risks to locations and affected entities when provided.

### 5.6 Metadata Storage

Implemented article metadata storage in Neo4j.

- Stores the complete metadata as a JSON string.
- Stores important metadata fields separately for easier querying.
- Preserves source severity independently from detected risk severity.
- Handles optional metadata values, including `null` values.

### 5.7 Transaction-Based Ingestion

Implemented Neo4j managed transactions using `session.execute_write()`.

This ensures that the database operations for an article are executed within a managed transaction.

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
- Risk-to-location relationship creation.

**Week 2 Result:** Successfully validated and ingested a GMRID article record into Neo4j AuraDB.

---

## 6. Current Backend Capabilities

| Feature | Status |
|---|---|
| Neo4j AuraDB connection | Completed |
| Supply-chain graph creation | Completed |
| Mock supply-chain data ingestion | Completed |
| GMRID JSON input support | Completed |
| JSON syntax validation | Completed |
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
| Dynamic NLP output integration | Pending |
| Multi-article ingestion testing | Pending |

---

## 7. Running the Backend

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

### Step 4: Validate an Article JSON File

```powershell
python backend/utils/json_validator.py backend/data/articles/sample_article.json
```

### Step 5: Ingest an Article into Neo4j

```powershell
python backend/database/article_ingest.py backend/data/articles/sample_article.json
```

You can replace the JSON file path with another GMRID-compatible article JSON file.

---

## 8. Current Development Status

Week 1 graph database foundations have been completed, including Neo4j AuraDB setup, supply-chain graph design, and automated mock data ingestion.

Week 2 focused on GMRID JSON integration and backend article processing. The JSON validator and article ingestion scripts have been updated to support the new input format. A sample article was successfully validated and ingested into Neo4j AuraDB.

The next development phase focuses on integrating dynamically generated NLP outputs, improving entity identification across multiple articles, and supporting prediction-related data in the graph.

---

## 9. Future Improvements

- Integrate dynamically generated NLP output.
- Establish a consistent entity identification strategy across articles.
- Support ingestion of multiple news articles.
- Improve article-level traceability for extracted entities and risks.
- Integrate prediction results into the Neo4j graph.
- Support backend APIs for frontend integration.
- Improve graph-based supply-chain risk analysis.

---

**AtmoGraph – Backend Development**

*Python | Neo4j AuraDB | Cypher | JSON*