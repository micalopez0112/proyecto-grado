from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from neo4j import GraphDatabase
import os


load_dotenv()
uri = os.getenv("MONGO_URI")

# MongoDB database
client = AsyncIOMotorClient(uri)
db = client.proyecto_grado

print("connected to db")
onto_collection = db.get_collection("ontologies")
mapping_process_collection = db.get_collection("mapping_process")
jsonschemas_collection = db.get_collection("json_schemas")

# Neo4j database settings
NEO_URI = os.getenv("NEO4J_URI")
NEO_USER = os.getenv("NEO4J_USERNAME")
NEO_PASS = os.getenv("NEO4J_PASSWORD")
## Neo4j database
class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self._driver.close()
    
    def get_driver(self):
        return self._driver

# Instancia única de conexión
neo4j_conn = Neo4jConnection(uri=NEO_URI, user=NEO_USER, password=NEO_PASS)