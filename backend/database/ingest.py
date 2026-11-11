
import json
from pathlib import Path

from connection import driver

# Locate the JSON file from the project root
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT_DIR / "backend" / "data" / "mock_supply_chain.json"

# Map JSON sections to Neo4j node labels
NODE_LABELS = {
    "suppliers": "Supplier",
    "factories": "Factory",
    "ports": "Port",
    "warehouses": "Warehouse",
    "retailers": "Retailer"
}

# Allow only the relationship types defined in our graph model
RELATIONSHIPS = {
    "SUPPLIES_TO": ("Supplier", "Factory"),
    "SHIPS_TO": ("Factory", "Port"),
    "TRANSPORTS_TO": ("Port", "Warehouse"),
    "DISTRIBUTES_TO": ("Warehouse", "Retailer")
}


def load_json():
    """Read supply-chain data from the JSON file."""
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def ingest_data(tx, data):
    """Insert or update nodes and relationships in Neo4j."""

    # Step 1: Create or match nodes
    for section, label in NODE_LABELS.items():

        for record in data[section]:
            query = f"""
            MERGE (n:{label} {{id: $id}})
            SET n += $properties
            """

            tx.run(
                query,
                id=record["id"],
                properties=record
            )

            print(f"Processed {label}: {record['id']}")

    # Step 2: Create or match relationships
    for relationship in data["relationships"]:

        rel_type = relationship["type"]

        if rel_type not in RELATIONSHIPS:
            raise ValueError(f"Unsupported relationship: {rel_type}")

        from_label, to_label = RELATIONSHIPS[rel_type]

        query = f"""
        MATCH (source:{from_label} {{id: $from_id}})
        MATCH (target:{to_label} {{id: $to_id}})
        MERGE (source)-[r:{rel_type}]->(target)
        SET r += $properties
        """

        properties = {
            key: value
            for key, value in relationship.items()
            if key not in ("type", "from_id", "to_id")
        }

        result = tx.run(
            query,
            from_id=relationship["from_id"],
            to_id=relationship["to_id"],
            properties=properties
        )

        result.consume()

        print(
            f"Processed relationship: "
            f"{relationship['from_id']} -[{rel_type}]-> "
            f"{relationship['to_id']}"
        )


def main():
    try:
        data = load_json()

        with driver.session() as session:
            session.execute_write(ingest_data, data)

        print("\nSupply-chain data ingestion completed successfully!")

    except Exception as error:
        print("\nData ingestion failed:", error)

    finally:
        driver.close()


if __name__ == "__main__":
    main()
