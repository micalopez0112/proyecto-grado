from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from neo4j import GraphDatabase

import os


load_dotenv()
uri = os.getenv("MONGO_URI")

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

neo4j_driver = None

def get_neo4j_driver():
    global neo4j_driver
    return neo4j_driver

def update_neo4j_driver(new_driver):
    global neo4j_driver
    neo4j_driver = new_driver

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = None
        self.connect(uri, user, password)
        # self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def connect(self, uri, user, password):
        if self._driver:
            self._driver.close()
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        update_neo4j_driver(self._driver)
        
    def close(self):
        self._driver.close()

    def get_driver(self):
        return self._driver

# Instancia única de conexión
neo4j_conn = Neo4jConnection(uri=NEO_URI, user=NEO_USER, password=NEO_PASS)





##call init governance zone
DLzone = os.getenv("ZONE_PATH")
print("DL ZONE EN DATABASE: ", DLzone)