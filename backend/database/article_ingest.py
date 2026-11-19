
import json
import sys
import uuid
from pathlib import Path

# Allow importing backend modules
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_DIR))

from database.connection import driver
from utils.json_validator import (
    validate_json,
    SUPPORTED_RELATIONSHIPS
)

# Default NLP JSON input file
DEFAULT_JSON_FILE = (
    BACKEND_DIR / "data" / "articles" / "sample_article.json"
)

# Convert NLP entity types into Neo4j labels
ENTITY_LABELS = {
    "GPE": "Location",
    "RISK": "Risk",
    "SHIPMENT": "Shipment",
    "ORG": "Organization"
}


def load_article(json_file):
    """Read the NLP output JSON file."""

    with open(json_file, "r", encoding="utf-8") as file:
        return json.load(file)


def prepare_entities(entities):
    """Preserve existing IDs and generate stable IDs when missing."""

    prepared_entities = []
    entity_ids = {}

    for entity in entities:

        entity_type = entity["type"]
        entity_name = entity["name"].strip()

        if entity_type not in ENTITY_LABELS:
            raise ValueError(
                f"Unsupported entity type: {entity_type}"
            )

        if not entity_name:
            raise ValueError("Entity name cannot be empty.")

        entity_id = entity.get("id")

        if not entity_id:

            unique_string = (
                f"atmograph:{entity_type}:{entity_name.casefold()}"
            )

            generated_uuid = uuid.uuid5(
                uuid.NAMESPACE_URL,
                unique_string
            )

            entity_id = f"AUTO_{generated_uuid.hex}"

            print(
                f"Generated ID for {entity_name}: {entity_id}"
            )

        prepared_entity = entity.copy()
        prepared_entity["id"] = entity_id
        prepared_entity["name"] = entity_name

        prepared_entities.append(prepared_entity)
        entity_ids[entity_name] = entity_id

    return prepared_entities, entity_ids


def ingest_entities(tx, entities):
    """Create or update entity nodes inside a transaction."""

    messages = []

    for entity in entities:

        label = ENTITY_LABELS[entity["type"]]

        query = f"""
        MERGE (e:{label} {{id: $id}})
        SET e.name = $name
        RETURN e.id AS entity_id
        """

        result = tx.run(
            query,
            id=entity["id"],
            name=entity["name"]
        )

        if result.single() is None:
            raise RuntimeError(
                f"Failed to create entity: {entity['name']}"
            )

        messages.append(
            f"Processed {label}: {entity['name']}"
        )

    return messages


def ingest_relationships(tx, entity_ids, relationships):
    """Create NLP relationships inside a transaction."""

    messages = []

    for relationship in relationships:

        name_1 = relationship["entity_1"].strip()
        name_2 = relationship["entity_2"].strip()
        relation = relationship["relation"]

        if relation not in SUPPORTED_RELATIONSHIPS:
            raise ValueError(
                f"Unsupported relationship type: {relation}"
            )

        id_1 = entity_ids.get(name_1)
        id_2 = entity_ids.get(name_2)

        if not id_1 or not id_2:
            raise ValueError(
                f"Unknown relationship entity: {name_1} -> {name_2}"
            )

        query = f"""
        MATCH (a {{id: $id_1}})
        MATCH (b {{id: $id_2}})
        MERGE (a)-[r:{relation}]->(b)
        SET r.evidence = $evidence
        RETURN type(r) AS relationship_type
        """

        result = tx.run(
            query,
            id_1=id_1,
            id_2=id_2,
            evidence=relationship.get("evidence", "")
        )

        if result.single() is None:
            raise RuntimeError(
                f"Could not create relationship: "
                f"{name_1} -[{relation}]-> {name_2}"
            )

        messages.append(
            f"Created relationship: "
            f"{name_1} -[{relation}]-> {name_2}"
        )

    return messages


def ingest_detected_risks(tx, entity_ids, detected_risks):
    """Update risks and create their associated relationships."""

    messages = []

    for risk_data in detected_risks:

        risk_name = risk_data["risk"].strip()
        risk_id = entity_ids.get(risk_name)

        if not risk_id:
            raise ValueError(
                f"Unknown risk entity: {risk_name}"
            )

        # Update risk properties
        result = tx.run("""
            MATCH (r:Risk {id: $risk_id})
            SET r.severity = $severity,
                r.evidence = $evidence
            RETURN r.id AS risk_id
        """,
            risk_id=risk_id,
            severity=risk_data["severity"],
            evidence=risk_data.get("evidence", "")
        )

        if result.single() is None:
            raise RuntimeError(
                f"Risk node not found: {risk_name}"
            )

        messages.append(
            f"Updated risk: {risk_name} | "
            f"Severity: {risk_data['severity']}"
        )

        # Connect risk to location
        location_name = risk_data.get("location")

        if isinstance(location_name, str) and location_name.strip():

            location_name = location_name.strip()
            location_id = entity_ids.get(location_name)

            if not location_id:
                raise ValueError(
                    f"Unknown location: {location_name}"
                )

            result = tx.run("""
                MATCH (r:Risk {id: $risk_id})
                MATCH (l:Location {id: $location_id})
                MERGE (r)-[:OCCURS_IN]->(l)
                RETURN r.id AS risk_id
            """,
                risk_id=risk_id,
                location_id=location_id
            )

            if result.single() is None:
                raise RuntimeError(
                    f"Could not connect risk to location: "
                    f"{location_name}"
                )

            messages.append(
                f"  Connected to location: {location_name}"
            )

        # Connect risk to affected entities
        for affected_name in risk_data.get("affected_entities", []):

            affected_name = affected_name.strip()
            affected_id = entity_ids.get(affected_name)

            if not affected_id:
                raise ValueError(
                    f"Unknown affected entity: {affected_name}"
                )

            result = tx.run("""
                MATCH (r:Risk {id: $risk_id})
                MATCH (e {id: $affected_id})
                MERGE (r)-[:AFFECTS]->(e)
                RETURN r.id AS risk_id
            """,
                risk_id=risk_id,
                affected_id=affected_id
            )

            if result.single() is None:
                raise RuntimeError(
                    f"Could not connect risk to affected entity: "
                    f"{affected_name}"
                )

            messages.append(
                f"  Affects: {affected_name}"
            )

    return messages


def ingest_article_transaction(tx, entities, entity_ids,
                               relationships, detected_risks):
    """
    Execute all article ingestion operations in one transaction.

    If any operation fails, Neo4j rolls back the transaction.
    """

    messages = []

    messages.extend(
        ingest_entities(tx, entities)
    )

    messages.extend(
        ingest_relationships(
            tx,
            entity_ids,
            relationships
        )
    )

    messages.extend(
        ingest_detected_risks(
            tx,
            entity_ids,
            detected_risks
        )
    )

    return messages


def main():
    """Validate and ingest an NLP article into Neo4j."""

    json_file = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else DEFAULT_JSON_FILE
    )

    if not json_file.is_absolute():
        json_file = Path.cwd() / json_file

    if not json_file.exists():
        print(f"JSON file not found: {json_file}")
        return

    # Step 1: Validate before database writes
    if not validate_json(json_file):
        print(
            "\nArticle ingestion cancelled "
            "due to validation errors."
        )
        return

    # Step 2: Load JSON
    try:
        data = load_article(json_file)

    except (json.JSONDecodeError, OSError) as error:
        print(f"Unable to load JSON file: {error}")
        return

    # Step 3: Prepare entities
    try:
        prepared_entities, entity_ids = prepare_entities(
            data["entities"]
        )

    except (ValueError, KeyError) as error:
        print(f"Entity preparation failed: {error}")
        return

    # Step 4: Execute one managed transaction
    try:
        with driver.session() as session:

            messages = session.execute_write(
                ingest_article_transaction,
                prepared_entities,
                entity_ids,
                data["relationships"],
                data["detected_risks"]
            )

        # Print success messages only after transaction commits
        for message in messages:
            print(message)

        print("\nArticle ingestion completed successfully!")

    except Exception as error:
        print("\nArticle ingestion failed!")
        print(f"Reason: {error}")
        print("Database transaction rolled back.")


if __name__ == "__main__":

    try:
        main()

    finally:
        driver.close()
