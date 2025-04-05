from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from neo4j import GraphDatabase

import os


load_dotenv()
uri = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(uri)
db = client.proyecto_grado

print("## connected to db ##")
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

def build_connection_string(uri, user, password):
    # Extraer host desde el URI proporcionado
    protocol, host = uri.split("://")
    return f"{protocol}://{user}:{password}@{host}"
#En nuestro caso:
# neo4j+s://{username}:{password}@5312230f.databases.neo4j.io


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

    def re_connect_local(self):
        if self._driver:
            self._driver.close()
        self._driver = GraphDatabase.driver(NEO_URI, auth=(NEO_USER, NEO_PASS))
        update_neo4j_driver(self._driver)
        print("Neo4j re-connected to local instance")
        
    def close(self):
        self._driver.close()

    def get_driver(self):
        return self._driver

# Instancia única de conexión
neo4j_conn = Neo4jConnection(uri=NEO_URI, user=NEO_USER, password=NEO_PASS)


##call init governance zone
DLzone = os.getenv("ZONE_PATH")
print("DL ZONE EN DATABASE: ", DLzone)