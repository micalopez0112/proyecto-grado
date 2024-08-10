from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from app.domain.mapping.models import MappingProcessDocument, get_mapping_process, MappingRequest, MappingResponse, OntologyDocument
from app.domain.mapping.service import process_mapping
from typing import Dict, Any
import motor.motor_asyncio
from bson import ObjectId
from owlready2 import get_ontology

import logging

router = APIRouter()
username = "Cluster04367"
password = "23deagosto8"
uri = 'mongodb+srv://' + username + ':' + password + '@cluster04367.44sngv1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster04367'

client = motor.motor_asyncio.AsyncIOMotorClient(uri)
db = client.proyecto_grado
jsonschemas_collection = db.get_collection("json_schemas")
mapping_process_collection = db.get_collection("mapping_process")
onto_collection = db.get_collection("ontologies")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/{mapping_proccess_id}", response_model=MappingResponse)
async def  save_mapping(id: str, request: MappingRequest = Body(...)):
    try:
      
        mapping_process_id = ObjectId(id)
        mapping_process_docu = await mapping_process_collection.find_one({'_id': mapping_process_id})
        if mapping_process_docu is None:
            raise HTTPException(status_code=404, detail="Mapping Process not found")
        
        # Validate the mapping field
        if not isinstance(request.mapping, dict):
            raise HTTPException(status_code=400, detail="The 'mapping' field must be a dictionary.")
        
        # Primero validamos el mapeo
        # obtengo la ontología
        ontologyFile = await onto_collection.find_one({'_id': ObjectId(mapping_process_docu['ontologyId'])})
        print("ontologyFile found correctly")
        ontologyFile['id'] = str(ontologyFile['_id'])
        ontology_document = OntologyDocument(**ontologyFile)
        if ontology_document.type == "FILE":
            ontology_path = ontology_document.file
            ontology = get_ontology(ontology_path).load()
        
        status = process_mapping(request.mapping, ontology)
        print("validation OK")
        # validto el mapping
        # Guardar esquema
        schema_dict = request.jsonSchema.dict(by_alias=True)
        schema_result = await jsonschemas_collection.insert_one(schema_dict)
        schema_id = schema_result.inserted_id
        print("hasta aca OK:")
        # Crear documento de mappingProcess con el mapping embebido
        mapping = request.mapping
        mapping_process_docu = MappingProcessDocument(mapping=mapping, jsonSchemaId=str(schema_id))
        print("hasta aca OK")
        result = await mapping_process_collection.update_one({'_id': mapping_process_id}, {'$set': mapping_process_docu.dict(exclude_unset=True)})

        print("mapping process updated correctly")
        return MappingResponse(message="Mapped successfully", status="success")
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