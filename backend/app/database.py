from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os


load_dotenv()
uri = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(uri)
db = client.proyecto_grado

print("connected to db")
onto_collection = db.get_collection("ontologies")
mapping_process_collection = db.get_collection("mapping_process")
jsonschemas_collection = db.get_collection("json_schemas")
