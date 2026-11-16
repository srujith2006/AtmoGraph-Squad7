
import json
import sys
import uuid
from pathlib import Path

# Allow importing the existing Neo4j connection module
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_DIR))

from database.connection import driver

# Default NLP JSON input file
DEFAULT_JSON_FILE = BACKEND_DIR / "data" / "articles" / "sample_article.json"

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
    """
    Preserve existing IDs and generate stable IDs for missing IDs.

    Returns:
        prepared_entities: Entities with IDs assigned.
        entity_ids: Mapping of entity names to IDs.
    """

    prepared_entities = []
    entity_ids = {}

    for entity in entities:

        entity_type = entity["type"]
        entity_name = entity["name"].strip()

        if entity_type not in ENTITY_LABELS:
            print(f"Skipping unsupported entity type: {entity_type}")
            continue

        if not entity_name:
            print("Skipping entity with empty name")
            continue

        # Preserve an existing ID
        entity_id = entity.get("id")

        # Generate a stable ID if one is missing
        if not entity_id:
            unique_string = f"atmograph:{entity_type}:{entity_name.casefold()}"

            generated_uuid = uuid.uuid5(
                uuid.NAMESPACE_URL,
                unique_string
            )

            entity_id = f"AUTO_{generated_uuid.hex}"

            print(f"Generated ID for {entity_name}: {entity_id}")

        # Create a new entity dictionary with its ID
        prepared_entity = entity.copy()
        prepared_entity["id"] = entity_id
        prepared_entity["name"] = entity_name

        prepared_entities.append(prepared_entity)
        entity_ids[entity_name] = entity_id

    return prepared_entities, entity_ids


def ingest_entities(session, entities):
    """Create entity nodes in Neo4j."""

    for entity in entities:

        entity_type = entity["type"]
        label = ENTITY_LABELS[entity_type]

        entity_id = entity["id"]
        entity_name = entity["name"]

        query = f"""
        MERGE (e:{label} {{id: $id}})
        SET e.name = $name
        """

        session.run(
            query,
            id=entity_id,
            name=entity_name
        ).consume()

        print(f"Processed {label}: {entity_name}")


def ingest_relationships(session, entity_ids, relationships):
    """Create relationships between existing entity nodes."""

    for relationship in relationships:

        name_1 = relationship["entity_1"]
        name_2 = relationship["entity_2"]
        relation = relationship["relation"]

        # Find IDs using the shared entity mapping
        id_1 = entity_ids.get(name_1)
        id_2 = entity_ids.get(name_2)

        if not id_1 or not id_2:
            print(f"Skipping relationship: {name_1} -> {name_2}")
            continue

        # Validate relationship type before using it in Cypher
        if not relation.isidentifier() or not relation.isupper():
            print(f"Invalid relationship type: {relation}")
            continue

        query = f"""
        MATCH (a {{id: $id_1}})
        MATCH (b {{id: $id_2}})
        MERGE (a)-[r:{relation}]->(b)
        SET r.evidence = $evidence
        """

        session.run(
            query,
            id_1=id_1,
            id_2=id_2,
            evidence=relationship.get("evidence", "")
        ).consume()

        print(f"Created relationship: {name_1} -[{relation}]-> {name_2}")


def ingest_detected_risks(session, entity_ids, detected_risks):
    """Add severity, location and affected entities to Risk nodes."""

    for risk_data in detected_risks:

        risk_name = risk_data["risk"]
        risk_id = entity_ids.get(risk_name)

        if not risk_id:
            print(f"Skipping unknown risk: {risk_name}")
            continue

        # Update severity and evidence
        session.run("""
            MATCH (r:Risk {id: $risk_id})
            SET r.severity = $severity,
                r.evidence = $evidence
        """,
            risk_id=risk_id,
            severity=risk_data["severity"],
            evidence=risk_data.get("evidence", "")
        ).consume()

        print(
            f"Updated risk: {risk_name} | "
            f"Severity: {risk_data['severity']}"
        )

        # Connect risk to its location, if available
        location_name = risk_data.get("location")
        location_id = entity_ids.get(location_name) if location_name else None

        if location_id:
            session.run("""
                MATCH (r:Risk {id: $risk_id})
                MATCH (l:Location {id: $location_id})
                MERGE (r)-[:OCCURS_IN]->(l)
            """,
                risk_id=risk_id,
                location_id=location_id
            ).consume()

            print(f"  Connected to location: {location_name}")

        # Connect risk to affected entities
        for affected_name in risk_data.get("affected_entities", []):

            affected_id = entity_ids.get(affected_name)

            if not affected_id:
                print(f"  Unknown affected entity: {affected_name}")
                continue

            session.run("""
                MATCH (r:Risk {id: $risk_id})
                MATCH (e {id: $affected_id})
                MERGE (r)-[:AFFECTS]->(e)
            """,
                risk_id=risk_id,
                affected_id=affected_id
            ).consume()

            print(f"  Affects: {affected_name}")


def main():
    """Run entity, relationship and risk ingestion."""

    # Accept a JSON file path from the command line
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

    try:
        data = load_article(json_file)

    except json.JSONDecodeError as error:
        print(f"Invalid JSON format: {error}")
        return

    except OSError as error:
        print(f"Unable to read JSON file: {error}")
        return

    # Step 1: Prepare entities and generate missing IDs
    prepared_entities, entity_ids = prepare_entities(data["entities"])

    with driver.session() as session:

        # Step 2: Create entity nodes
        ingest_entities(session, prepared_entities)

        # Step 3: Create relationships
        ingest_relationships(
            session,
            entity_ids,
            data["relationships"]
        )

        # Step 4: Process detected risks
        ingest_detected_risks(
            session,
            entity_ids,
            data["detected_risks"]
        )

    print("\nArticle ingestion completed successfully!")


if __name__ == "__main__":
    try:
        main()
    finally:
        driver.close()
