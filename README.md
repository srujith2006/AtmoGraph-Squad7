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

## 5. Week 2 – NLP Output Integration and Backend Processing

### 5.1 Dynamic JSON Input

Implemented article ingestion that accepts JSON files through command-line arguments instead of relying on a fixed input file.

Example:

```powershell
python backend/database/article_ingest.py backend/data/articles/sample_article.json
```

### 5.2 JSON Validation

Developed `json_validator.py` to validate incoming NLP JSON data before database ingestion.

Validation includes:

- JSON syntax verification.
- Required field verification.
- Entity type validation.
- Duplicate entity ID and name checks.
- Relationship type validation.
- Entity reference verification.
- Risk severity validation.
- Detected risk and affected entity validation.

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

Supported severity levels:

- `LOW`
- `MEDIUM`
- `HIGH`

### 5.3 Automatic Entity ID Generation

Implemented automatic ID generation for entities that do not contain an ID in the incoming JSON.

- Existing IDs are preserved.
- Missing IDs are generated using deterministic UUID generation.
- Generated IDs use the `AUTO_` prefix.
- Entity names and types are used to generate consistent IDs.

This allows the backend to process JSON data even when the NLP output does not provide entity IDs.

### 5.4 Neo4j Article Ingestion

Implemented `article_ingest.py` to process NLP-generated JSON data.

The ingestion process:

1. Loads the JSON article.
2. Validates the input.
3. Prepares entity IDs.
4. Creates or updates entity nodes.
5. Creates relationships between entities.
6. Updates detected risk information.
7. Connects risks to locations and affected entities.

### 5.5 Transaction Safety

Implemented Neo4j managed transactions using `session.execute_write()`.

This ensures that all database operations for an article are treated as a single transaction.

- Successful ingestion commits all changes.
- If an operation fails, the transaction is rolled back.
- Prevents partially ingested article data.

### 5.6 Duplicate Handling

Used Cypher `MERGE` operations to avoid unnecessary duplicate nodes and relationships during repeated ingestion.

Verified node and relationship counts after repeated ingestion.

### 5.7 NLP Team Output Integration

Successfully tested the backend using the JSON output received from the NLP development team.

The test included:

- Singapore as a geographical entity.
- Port congestion and shipment delay as risks.
- Semiconductor shipments as a shipment entity.
- Samsung and Intel as organizations.
- Relationships between the extracted entities.
- Risk severity and affected entity information.

**Integration Result:** JSON validation and Neo4j article ingestion completed successfully using the team's static sample dataset.

---

## 6. Current Backend Capabilities

| Feature | Status |
|---|---|
| Neo4j AuraDB connection | Completed |
| Supply-chain graph creation | Completed |
| Mock data ingestion | Completed |
| Dynamic JSON file input | Completed |
| JSON validation | Completed |
| Automatic entity ID generation | Completed |
| Entity and relationship ingestion | Completed |
| Risk information ingestion | Completed |
| Duplicate handling | Tested |
| Transaction safety | Tested |
| Rollback verification | Passed |
| NLP team JSON integration | Tested with static dataset |
| Dynamic NLP output integration | Pending |
| Multi-article ID management | Pending |

---

## 7. Running the Backend

### Step 1: Install dependencies

```powershell
pip install neo4j python-dotenv certifi
```

### Step 2: Configure environment variables

Create a `.env` file in the project root using `.env.example` as a reference.

Configure:

```env
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
```

Do not commit the `.env` file to GitHub.

### Step 3: Configure SSL certificate path

For PowerShell:

```powershell
$env:SSL_CERT_FILE = python -c "import certifi; print(certifi.where())"
```

### Step 4: Validate an article JSON file

```powershell
python backend/utils/json_validator.py backend/data/articles/sample_article.json
```

### Step 5: Ingest an article into Neo4j

```powershell
python backend/database/article_ingest.py backend/data/articles/sample_article.json
```

You can replace the JSON file path with another article JSON file.

---

## 8. Current Development Status

Week 1 graph database foundations have been completed.

Week 2 backend processing features have been implemented and tested, including JSON validation, automatic entity ID generation, article ingestion, transaction safety, and integration with the NLP team's current static JSON output.

The next development phase focuses on integrating dynamically generated NLP outputs, establishing a reliable entity ID strategy across multiple articles, and supporting multi-article ingestion.

---

## 9. Future Improvements

- Integrate dynamically generated NLP output.
- Establish a collision-safe entity ID strategy across articles.
- Support ingestion of multiple news articles.
- Maintain article-level traceability for extracted entities and risks.
- Support backend APIs for frontend integration.
- Improve graph-based supply-chain risk analysis.

---

**AtmoGraph – Backend Development**  
*Python | Neo4j AuraDB | Cypher | JSON*