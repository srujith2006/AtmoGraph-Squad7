
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Find the project root directory
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

# Load credentials from the project root .env file
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# Read Neo4j credentials
URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# Validate configuration
if not URI or not USERNAME or not PASSWORD:
    raise RuntimeError(
        "Neo4j configuration is incomplete. "
        "Check NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD "
        "in your project .env file."
    )

# Create Neo4j driver
driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def test_connection():
    """Test Neo4j AuraDB connectivity and retrieve node count."""

    try:
        # Verify database connectivity
        driver.verify_connectivity()

        print("Successfully connected to Neo4j AuraDB!")

        # Execute a test Cypher query
        with driver.session() as session:
            result = session.run("""
                MATCH (n)
                RETURN count(n) AS total_nodes
            """)

            record = result.single()

            if record is not None:
                count = record["total_nodes"]
                print("Total nodes in database:", count)
            else:
                print("No result returned from Neo4j.")

    except Exception as error:
        print("Connection failed:", error)


if __name__ == "__main__":
    try:
        test_connection()
    finally:
        driver.close()
