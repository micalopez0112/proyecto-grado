from fastapi import APIRouter, HTTPException, UploadFile, File, Body
import motor.motor_asyncio
from bson import ObjectId
from owlready2 import get_ontology
from typing import Dict, Any
from app.domain.mapping.models import MappingProcessDocument, get_mapping_process, MappingRequest, MappingResponse, OntologyDocument
from app.domain.mapping.service import process_mapping
from ..database import onto_collection, mapping_process_collection, jsonschemas_collection

router = APIRouter()

@router.post("/ontology_id/{ontology_id}", response_model=MappingResponse)
async def  save_mapping(id: str, request: MappingRequest = Body(...)):
    try:
        ontology_id = ObjectId(id)
        ontology_docu = await onto_collection.find_one({'_id': ontology_id})
        
        if ontology_docu is None:
            raise HTTPException(status_code=404, detail="Ontology not found")
        
        # Validate the mapping field
        if not isinstance(request.mapping, dict):
            raise HTTPException(status_code=400, detail="Invalid mapping body")
        
        ontology_docu['id'] = str(ontology_docu['_id'])
        ontology_document = OntologyDocument(**ontology_docu)
        if ontology_document.type == "FILE":
            ontology_path = ontology_document.file
            ontology = get_ontology(ontology_path).load()
        
        # here we validate if the mapping is correct
        status = process_mapping(request.mapping, ontology)
        print("validation OK")

        # saving json schema
        schema_dict = request.jsonSchema.dict(by_alias=True)
        schema_result = await jsonschemas_collection.insert_one(schema_dict)
        schema_id = schema_result.inserted_id

        # saving mapping process
        mapping = request.mapping
        mapping_process_docu = MappingProcessDocument(mapping=mapping, ontologyId=id,jsonSchemaId=str(schema_id))
        mapping_pr_id = await mapping_process_collection.insert_one(mapping_process_docu.dict(exclude_unset=True))

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