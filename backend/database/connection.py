
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load credentials
load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# Create Neo4j driver
driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

def test_connection():
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
