from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from app.domain.mapping.models import MappingProcess, get_mapping_process, MappingRequest, MappingResponse
from app.domain.mapping.service import process_mapping
from typing import Dict, Any
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import motor.motor_asyncio
import json
import logging

router = APIRouter()
username = "Cluster04367"
password = "23deagosto8"
uri = 'mongodb+srv://' + username + ':' + password + '@cluster04367.44sngv1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster04367'

#uri = "mongodb+srv://Cluster04367:<password>@cluster04367.44sngv1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster04367"
# Mongo client and collections
#client = MongoClient(uri, server_api=ServerApi('1'))
client = motor.motor_asyncio.AsyncIOMotorClient(uri)
db = client.college
onto_collection = db.get_collection("ontologies")
jsonschemas_collection = db.get_collection("schemas")
mapping_process_collection = db.get_collection("mapping_process")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/", response_model=MappingResponse)
async def  save_mapping(
    ontology_file: UploadFile = File(...),
    request: MappingRequest = Body(...)
):
    print("HOLA")
    try:
          # Log the received data
        logger.info(f"Received mapping: {request.mapping}")
        logger.info(f"Received jsonSchema: {request.jsonSchema}")

        # Validate the mapping field
        if not isinstance(request.mapping, dict):
            raise HTTPException(status_code=400, detail="The 'mapping' field must be a dictionary.")

        # Guardar ontología
        # Leer y guardar ontología
        ontology_content = await ontology_file.read()
        ontology_json = json.loads(ontology_content.decode('utf-8'))
        ontology_result = onto_collection.insert_one(ontology_json)
        ontology_id = ontology_result.inserted_id

        # Guardar esquema
        schema_dict = request.jsonSchema.dict(by_alias=True)
        schema_result = await jsonschemas_collection.insert_one(schema_dict)
        schema_id = schema_result.inserted_id
        print("hasta aca OK:")
        # Crear documento de mappingProcess con el mapping embebido
        mapping_process = {
            "ontology_id": ontology_id,
            "mapping": request.mapping,
            "jsonSchema_id": schema_id
        }
        mapping_process_result = mapping_process_collection.insert_one(mapping_process)
        mapping_process_id = mapping_process_result.inserted_id

        return {"mapping_process_id": str(mapping_process_id)}
    except Exception as e:
        print("Error saving mapping process:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{process_id}", response_model=MappingResponse)
def get_mapping(process_id: int, mapRequestBody: MappingRequest):
    mappingProcess = get_mapping_process(process_id)
    mappingProcess.mapping = mapRequestBody.mapping
    print("Starting mapping process:", mappingProcess)
    try :
        status = process_mapping(mappingProcess)
    except ValueError as e:
        msg = str(e)
        status = "error"
        response = MappingResponse(message=msg, status="error")
        return response
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response

    return MappingResponse(message="Mapped successfully", status="success")