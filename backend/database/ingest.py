
"""Load mock supply-chain records and merge them into the Neo4j graph."""

import json
from pathlib import Path

from connection import driver  # Shared Neo4j driver configured from environment variables.

# Resolve the repository root so this script works regardless of the current directory.
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT_DIR / "backend" / "data" / "mock_supply_chain.json"

# Connect each top-level JSON collection to its corresponding Neo4j node label.
NODE_LABELS = {
    "suppliers": "Supplier",
    "factories": "Factory",
    "ports": "Port",
    "warehouses": "Warehouse",
    "retailers": "Retailer"
}

# Whitelist relationship types and their required source/target node labels.
RELATIONSHIPS = {
    "SUPPLIES_TO": ("Supplier", "Factory"),
    "SHIPS_TO": ("Factory", "Port"),
    "TRANSPORTS_TO": ("Port", "Warehouse"),
    "DISTRIBUTES_TO": ("Warehouse", "Retailer")
}


def load_json():
    """Read and parse the mock supply-chain dataset from disk."""
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def ingest_data(tx, data):
    """Merge all dataset nodes and relationships inside the caller transaction."""

    # Merge nodes by ID so rerunning ingestion updates records instead of duplicating them.
    for section, label in NODE_LABELS.items():

        for record in data[section]:
            # Labels come from the fixed NODE_LABELS map; values are passed as parameters.
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

    # Merge edges by endpoints and type, then apply their non-key properties.
    for relationship in data["relationships"]:

        rel_type = relationship["type"]

        # Reject unknown types before constructing a Cypher query.
        if rel_type not in RELATIONSHIPS:
            raise ValueError(f"Unsupported relationship: {rel_type}")

        from_label, to_label = RELATIONSHIPS[rel_type]

        query = f"""
        MATCH (source:{from_label} {{id: $from_id}})
        MATCH (target:{to_label} {{id: $to_id}})
        MERGE (source)-[r:{rel_type}]->(target)
        SET r += $properties
        """

        # Keep relationship metadata separate from the endpoint and type identifiers.
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
    """Load the dataset, run one write transaction, and always close the driver."""
    try:
        data = load_json()

        # The transaction helper commits on success and rolls back if ingestion raises.
        with driver.session() as session:
            session.execute_write(ingest_data, data)

        print("\nSupply-chain data ingestion completed successfully!")

    except Exception as error:
        print("\nData ingestion failed:", error)

    finally:
        driver.close()


if __name__ == "__main__":
    main()
