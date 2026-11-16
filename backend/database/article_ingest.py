
import json
import sys
from pathlib import Path

# Allow importing the existing Neo4j connection module
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_DIR))

from database.connection import driver

# NLP JSON input file
JSON_FILE = BACKEND_DIR / "data" / "articles" / "sample_article.json"

# Convert NLP entity types into Neo4j labels
ENTITY_LABELS = {
    "GPE": "Location",
    "RISK": "Risk",
    "SHIPMENT": "Shipment",
    "ORG": "Organization"
}


def load_article():
    """Read the NLP output JSON file."""
    with open(JSON_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def ingest_entities(session, entities):
    """Create entity nodes in Neo4j."""

    for entity in entities:
        entity_type = entity["type"]
        label = ENTITY_LABELS.get(entity_type)

        if label is None:
            print(f"Skipping unsupported entity type: {entity_type}")
            continue

        entity_id = entity.get("id")
        entity_name = entity["name"]

        if not entity_id:
            print(f"Skipping entity without ID: {entity_name}")
            continue

        query = f"""
        MERGE (e:{label} {{id: $id}})
        SET e.name = $name
        """

        session.run(
            query,
            id=entity_id,
            name=entity_name
        )

        print(f"Processed {label}: {entity_name}")


def ingest_relationships(session, entities, relationships):
    """Create relationships between existing entity nodes."""

    # Map entity names to their IDs
    entity_ids = {
        entity["name"]: entity["id"]
        for entity in entities
        if entity.get("id")
    }

    for relationship in relationships:
        name_1 = relationship["entity_1"]
        name_2 = relationship["entity_2"]
        relation = relationship["relation"]

        # Find IDs using entity names
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

        result = session.run(
            query,
            id_1=id_1,
            id_2=id_2,
            evidence=relationship.get("evidence", "")
        )

        result.consume()

        print(f"Created relationship: {name_1} -[{relation}]-> {name_2}")



def ingest_detected_risks(session, entities, detected_risks):
    """Add severity, location and affected entities to Risk nodes."""

    # Map entity names to their IDs
    entity_ids = {
        entity["name"]: entity["id"]
        for entity in entities
        if entity.get("id")
    }

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

        print(f"Updated risk: {risk_name} | Severity: {risk_data['severity']}")

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

    data = load_article()

    with driver.session() as session:

        # Step 1: Create entity nodes
        ingest_entities(session, data["entities"])

        # Step 2: Create relationships
        ingest_relationships(
            session,
            data["entities"],
            data["relationships"]
        )

        # Step 3: Process detected risks
        ingest_detected_risks(
            session,
            data["entities"],
            data["detected_risks"]
        )

    print("\nArticle ingestion completed successfully!")


if __name__ == "__main__":
    try:
        main()
    finally:
        driver.close()