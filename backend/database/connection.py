
"""Configure the Neo4j driver and provide a small connectivity check."""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load database credentials from the repository-root .env file into the process environment.
load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# Create the shared driver used by the database scripts.
driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

def test_connection():
    """Verify the Neo4j connection and print the current node count."""
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

            count = result.single()["total_nodes"]

            print("Total nodes in database:", count)

    except Exception as error:
        print("Connection failed:", error)

    finally:
        driver.close()


if __name__ == "__main__":
    test_connection()
