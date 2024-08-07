from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.routers.mapping import router as mapping_router
from app.routers.ontology import router as ontology_router
from app.routers.json_schema import router as jsonschema_router
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

origins = ['http://localhost:3000']

uri = "mongodb+srv://Cluster04367:<password>@cluster04367.44sngv1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster04367"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mapping_router, prefix="/mapping", tags=["mappings"])
app.include_router(ontology_router, prefix="/ontologies", tags=["ontologies"])
app.include_router(jsonschema_router, prefix="/jsonschema", tags=["jsonschema"])
