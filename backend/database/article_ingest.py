
import json
import sys
import uuid
from pathlib import Path

# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_DIR))

from database.connection import driver
from utils.json_validator import (
    validate_dataset,
    SUPPORTED_RELATIONSHIP_TYPES
)

DEFAULT_JSON_FILE = (
    BACKEND_DIR / "data" / "articles" / "team_output.json"
)


# --------------------------------------------------
# ENTITY CONFIGURATION
# --------------------------------------------------

ENTITY_LABELS = {
    "REGION": "Region",
    "LOCATION": "Location",
    "PORT": "Port"
}


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def normalize_name(name):
    """Normalize names for consistent entity matching."""
    return name.strip().casefold()


def generate_stable_id(category, value):
    """Generate a deterministic ID for a Neo4j node."""

    unique_string = f"atmograph:{category}:{value}"

    generated_uuid = uuid.uuid5(
        uuid.NAMESPACE_URL,
        unique_string
    )

    return generated_uuid.hex


def load_json_file(json_file):
    """Load JSON data from the supplied file."""

    with open(json_file, "r", encoding="utf-8") as file:
        return json.load(file)


def prepare_entities(entities):
    """
    Prepare entities with stable IDs.

    Creates a lookup using normalized names.
    Duplicate entities with the same type and name
    are stored only once per article.
    """

    prepared_entities = []
    entity_index = {}
    seen_entities = set()

    for entity in entities:

        entity_type = entity["type"]
        entity_name = entity["name"].strip()

        if entity_type not in ENTITY_LABELS:
            raise ValueError(
                f"Unsupported entity type: {entity_type}"
            )

        if not entity_name:
            continue

        normalized_name = normalize_name(entity_name)

        entity_id = generate_stable_id(
            entity_type,
            normalized_name
        )

        unique_key = (entity_type, normalized_name)

        if unique_key in seen_entities:
            continue

        seen_entities.add(unique_key)

        prepared_entity = {
            "id": entity_id,
            "name": entity_name,
            "normalized_name": normalized_name,
            "type": entity_type
        }

        prepared_entities.append(prepared_entity)

        entity_index.setdefault(
            normalized_name, []
        ).append(prepared_entity)

    return prepared_entities, entity_index


def resolve_entity(entity_index, name):
    """
    Find an entity by normalized name.

    Returns an entity only when exactly one match exists.
    Ambiguous names are not connected automatically.
    """

    if not isinstance(name, str) or not name.strip():
        return None

    matches = entity_index.get(normalize_name(name), [])

    if len(matches) == 1:
        return matches[0]

    return None


# --------------------------------------------------
# ARTICLE NODE INGESTION
# --------------------------------------------------

def ingest_article_node(tx, article_data):
    """Create or update an Article node."""

    metadata = article_data["metadata"]
    gpt_label = metadata.get("gpt_4o_label") or {}

    properties = {
        "record_id": article_data["record_id"],
        "source": article_data["source"],
        "text": article_data["article"],
        "severity_note": article_data.get("severity_note"),

        # Preserve complete original data
        "metadata_json": json.dumps(
            metadata,
            ensure_ascii=False
        ),

        "raw_fields_json": json.dumps(
            article_data.get("raw_fields", {}),
            ensure_ascii=False
        ),

        "risk_review_candidates_previous_json": json.dumps(
            article_data.get("risk_review_candidates_previous", []),
            ensure_ascii=False
        ),

        "detected_risks_initial_json": json.dumps(
            article_data.get("detected_risks_initial", []),
            ensure_ascii=False
        ),

        # Flatten frequently used metadata
        "date": metadata.get("date"),
        "region": metadata.get("region"),
        "latitude": metadata.get("latitude"),
        "longitude": metadata.get("longitude"),
        "maritime_label": metadata.get("maritime_label"),
        "found_ports": metadata.get("found_ports", []),
        "contains_port_info": metadata.get("contains_port_info"),
        "if_labeled": metadata.get("if_labeled"),
        "year": metadata.get("year"),
        "month": metadata.get("month"),
        "week": metadata.get("week"),
        "category": metadata.get("category"),
        "summarized_label": metadata.get("summarized_label"),
        "gpt_4o_category": gpt_label.get("category"),
        "gpt_4o_specific_tags": gpt_label.get(
            "specific_tags", []
        ),
        "source_severity": metadata.get("source_severity")
    }

    result = tx.run(
        """
        MERGE (a:Article {record_id: $record_id})
        SET a += $properties
        RETURN a.record_id AS record_id
        """,
        record_id=article_data["record_id"],
        properties=properties
    )

    if result.single() is None:
        raise RuntimeError(
            "Failed to create Article node."
        )


# --------------------------------------------------
# ENTITY NODE INGESTION
# --------------------------------------------------

def ingest_entities(tx, record_id, entities):
    """Create entity nodes and connect them to the article."""

    for entity in entities:

        label = ENTITY_LABELS[entity["type"]]

        query = f"""
        MERGE (e:{label} {{entity_id: $entity_id}})
        SET e.name = $name,
            e.normalized_name = $normalized_name,
            e.entity_type = $entity_type

        WITH e
        MATCH (a:Article {{record_id: $record_id}})
        MERGE (a)-[:MENTIONS]->(e)

        RETURN e.entity_id AS entity_id
        """

        result = tx.run(
            query,
            entity_id=entity["id"],
            name=entity["name"],
            normalized_name=entity["normalized_name"],
            entity_type=entity["type"],
            record_id=record_id
        )

        if result.single() is None:
            raise RuntimeError(
                f"Failed to ingest entity: {entity['name']}"
            )


# --------------------------------------------------
# PORT INGESTION
# --------------------------------------------------

def ingest_ports(tx, article_data):
    """
    Create Port nodes from metadata.found_ports.

    These are stored as port mentions.
    Their presence does not imply that a port is affected.
    """

    record_id = article_data["record_id"]

    for port_name in article_data["metadata"].get(
        "found_ports", []
    ):

        port_name = port_name.strip()

        if not port_name:
            continue

        normalized_name = normalize_name(port_name)

        port_id = generate_stable_id(
            "PORT",
            normalized_name
        )

        result = tx.run(
            """
            MERGE (p:Port {entity_id: $port_id})
            SET p.name = $port_name,
                p.normalized_name = $normalized_name,
                p.entity_type = 'PORT'

            WITH p
            MATCH (a:Article {record_id: $record_id})
            MERGE (a)-[:MENTIONS_PORT]->(p)

            RETURN p.entity_id AS port_id
            """,
            port_id=port_id,
            port_name=port_name,
            normalized_name=normalized_name,
            record_id=record_id
        )

        if result.single() is None:
            raise RuntimeError(
                f"Failed to connect article to port: {port_name}"
            )


# --------------------------------------------------
# NLP RELATIONSHIP INGESTION
# --------------------------------------------------

def ingest_relationships(
    tx,
    record_id,
    entity_index,
    relationships
):
    """
    Create relationships between extracted entities.

    Relationship endpoints are matched by name.
    Ambiguous or missing endpoints are skipped with warnings.
    """

    warnings = []

    for relationship in relationships:

        source_name = relationship["source"].strip()
        target_name = relationship["target"].strip()
        relation_type = relationship["relationship"]

        if relation_type not in SUPPORTED_RELATIONSHIP_TYPES:
            raise ValueError(
                f"Unsupported relationship: {relation_type}"
            )

        source_entity = resolve_entity(
            entity_index, source_name
        )

        target_entity = resolve_entity(
            entity_index, target_name
        )

        if source_entity is None or target_entity is None:

            warnings.append(
                f"Skipped unresolved/ambiguous relationship: "
                f"{source_name} -> {target_name}"
            )
            continue

        # Relationship type comes only from the validator allowlist.
        query = f"""
        MATCH (s {{entity_id: $source_id}})
        MATCH (t {{entity_id: $target_id}})
        MATCH (a:Article {{record_id: $record_id}})

        MERGE (s)-[r:{relation_type}]->(t)
        SET r.evidence = $evidence

        MERGE (a)-[:HAS_RELATIONSHIP]->(s)
        MERGE (a)-[:HAS_RELATIONSHIP]->(t)

        RETURN type(r) AS relationship_type
        """

        result = tx.run(
            query,
            source_id=source_entity["id"],
            target_id=target_entity["id"],
            record_id=record_id,
            evidence=relationship.get("evidence")
        )

        if result.single() is None:
            raise RuntimeError(
                f"Could not create relationship: "
                f"{source_name} -[{relation_type}]-> {target_name}"
            )

    return warnings


# --------------------------------------------------
# DETECTED RISK INGESTION
# --------------------------------------------------

def ingest_detected_risks(
    tx,
    record_id,
    entity_index,
    detected_risks
):
    """
    Ingest confirmed detected risks.

    Risk severity and evidence are stored on the
    article-to-risk relationship to avoid overwriting
    information from other articles.
    """

    warnings = []

    for risk_data in detected_risks:

        risk_name = risk_data["risk"].strip()

        if not risk_name:
            continue

        risk_id = generate_stable_id(
            "RISK",
            normalize_name(risk_name)
        )

        result = tx.run(
            """
            MERGE (r:Risk {risk_id: $risk_id})
            SET r.name = $risk_name

            WITH r
            MATCH (a:Article {record_id: $record_id})

            MERGE (a)-[dr:HAS_DETECTED_RISK {
                risk_id: $risk_id
            }]->(r)

            SET dr.severity = $severity,
                dr.evidence = $evidence,
                dr.location = $location

            RETURN r.risk_id AS risk_id
            """,
            risk_id=risk_id,
            risk_name=risk_name,
            record_id=record_id,
            severity=risk_data["severity"],
            evidence=risk_data.get("evidence"),
            location=risk_data.get("location")
        )

        if result.single() is None:
            raise RuntimeError(
                f"Failed to ingest detected risk: {risk_name}"
            )

        # Connect risk to a location only if the
        # location matches exactly one extracted entity.
        location_name = risk_data.get("location")

        if isinstance(location_name, str) and location_name.strip():

            location_entity = resolve_entity(
                entity_index,
                location_name
            )

            if location_entity is None:

                warnings.append(
                    f"Risk location not linked because it was "
                    f"unresolved or ambiguous: {location_name}"
                )

            elif location_entity["type"] in {
                "LOCATION", "PORT"
            }:

                tx.run(
                    """
                    MATCH (r:Risk {risk_id: $risk_id})
                    MATCH (l {entity_id: $location_id})
                    MERGE (r)-[:OCCURS_IN]->(l)
                    """,
                    risk_id=risk_id,
                    location_id=location_entity["id"]
                )

    return warnings


# --------------------------------------------------
# RISK REVIEW CANDIDATE INGESTION
# --------------------------------------------------

def ingest_risk_review_candidates(
    tx,
    record_id,
    candidates
):
    """
    Store review candidates separately from confirmed risks.

    CANDIDATE, NEEDS_REVIEW and CONTRADICTED
    are preserved as their original statuses.
    """

    for index, candidate in enumerate(candidates):

        risk_name = candidate["risk"].strip()

        candidate_id = generate_stable_id(
            "RISK_REVIEW_CANDIDATE",
            f"{record_id}:{index}"
        )

        result = tx.run(
            """
            MERGE (c:RiskReviewCandidate {
                candidate_id: $candidate_id
            })

            SET c.risk = $risk,
                c.location = $location,
                c.source_locations_json = $source_locations_json,
                c.severity = $severity,
                c.evidence = $evidence,
                c.status = $status

            WITH c
            MATCH (a:Article {record_id: $record_id})
            MERGE (a)-[:HAS_REVIEW_CANDIDATE]->(c)

            RETURN c.candidate_id AS candidate_id
            """,
            candidate_id=candidate_id,
            risk=risk_name,
            location=candidate.get("location"),
            source_locations_json=json.dumps(
                candidate.get("source_locations", []),
                ensure_ascii=False
            ),
            severity=candidate["severity"],
            evidence=candidate.get("evidence"),
            status=candidate["status"],
            record_id=record_id
        )

        if result.single() is None:
            raise RuntimeError(
                f"Failed to ingest review candidate: {risk_name}"
            )


# --------------------------------------------------
# COMPLETE ARTICLE TRANSACTION
# --------------------------------------------------

def ingest_article_transaction(tx, article_data):
    """
    Ingest one complete article in a single transaction.

    If any critical operation fails, this article's
    transaction is rolled back.
    """

    record_id = article_data["record_id"]

    entities, entity_index = prepare_entities(
        article_data["entities"]
    )

    # 1. Create or update Article
    ingest_article_node(tx, article_data)

    # 2. Create extracted entity nodes
    ingest_entities(tx, record_id, entities)

    # 3. Create port mentions
    ingest_ports(tx, article_data)

    # 4. Create NLP relationships
    warnings = ingest_relationships(
        tx,
        record_id,
        entity_index,
        article_data["relationships"]
    )

    # 5. Ingest confirmed risks
    warnings.extend(
        ingest_detected_risks(
            tx,
            record_id,
            entity_index,
            article_data["detected_risks"]
        )
    )

    # 6. Store review candidates separately
    ingest_risk_review_candidates(
        tx,
        record_id,
        article_data["risk_review_candidates"]
    )

    return warnings


# --------------------------------------------------
# MAIN BATCH INGESTION
# --------------------------------------------------

def main():

    json_file = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else DEFAULT_JSON_FILE
    )

    if not json_file.is_absolute():
        json_file = Path.cwd() / json_file

    print("\n========== ATMOGRAPH BATCH INGESTION ==========")
    print(f"Input file: {json_file}")

    if not json_file.exists():
        print("\nERROR: JSON file not found.")
        return

    # Step 1: Load JSON
    try:
        data = load_json_file(json_file)

    except (json.JSONDecodeError, OSError) as error:
        print(f"\nUnable to load JSON: {error}")
        return

    # Step 2: Validate entire dataset before database writes
    valid_records, errors = validate_dataset(data)

    total_records = len(data) if isinstance(data, list) else 1

    print(f"\nTotal records: {total_records}")
    print(f"Valid records: {len(valid_records)}")
    print(f"Validation errors: {len(errors)}")

    if errors:

        print("\nINGESTION CANCELLED.")
        print("Fix validation errors before database ingestion.")

        for error in errors[:30]:
            print(f"- {error}")

        if len(errors) > 30:
            print(f"... and {len(errors) - 30} more errors.")

        return

    # Step 3: Connect to Neo4j
    try:
        driver.verify_connectivity()
        print("\nNeo4j connection successful.")

    except Exception as error:
        print("\nNeo4j connection failed.")
        print(f"Reason: {error}")
        return

    # Step 4: Ingest each article independently
    successful_records = 0
    failed_records = 0
    total_warnings = 0

    for index, article_data in enumerate(valid_records, start=1):

        record_id = article_data["record_id"]

        try:

            with driver.session() as session:

                warnings = session.execute_write(
                    ingest_article_transaction,
                    article_data
                )

            successful_records += 1
            total_warnings += len(warnings)

            if index % 50 == 0 or index == total_records:
                print(
                    f"Progress: {index}/{total_records} "
                    f"| Successful: {successful_records} "
                    f"| Failed: {failed_records}"
                )

            for warning in warnings:
                print(
                    f"WARNING | Record {record_id}: {warning}"
                )

        except Exception as error:

            failed_records += 1

            print(
                f"\nFAILED | Record {record_id}: {error}"
            )

    # Step 5: Final report
    print("\n========== INGESTION SUMMARY ==========")
    print(f"Total records: {total_records}")
    print(f"Successful records: {successful_records}")
    print(f"Failed records: {failed_records}")
    print(f"Relationship/location warnings: {total_warnings}")

    if failed_records == 0:
        print("\nBATCH INGESTION COMPLETED.")
    else:
        print("\nBATCH INGESTION COMPLETED WITH ERRORS.")


# --------------------------------------------------
# EXECUTION
# --------------------------------------------------

if __name__ == "__main__":

    try:
        main()

    finally:
        driver.close()
