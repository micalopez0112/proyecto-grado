from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from bson import ObjectId
from owlready2 import get_ontology
import motor.motor_asyncio
from typing import Dict, Any
from app.domain.mapping.utils import get_ontology_info_from_pid, graph_generator
from app.domain.mapping.models import MappingProcessDocument, get_mapping_process, MappingRequest, MappingResponse, OntologyDocument
from app.domain.mapping.service import process_mapping
from ..database import onto_collection, mapping_process_collection, jsonschemas_collection

router = APIRouter()

@router.post("/ontology_id/{id}", response_model=MappingResponse)
async def save_mapping(id: str, request: MappingRequest = Body(...)):
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
        mapping_process_docu = MappingProcessDocument(name=request.mapping_name, mapping=mapping, ontologyId=id,jsonSchemaId=str(schema_id))
        mapping_pr_id = await mapping_process_collection.insert_one(mapping_process_docu.dict(exclude_unset=True))

        return MappingResponse(message="Mapped successfully", status="success",mapping_id=str(mapping_pr_id.inserted_id))
    except ValueError as e:
        msg = str(e)
        status = "error"
        response = MappingResponse(message=msg, status="error")
        return response
    except Exception as e:
        print("Error saving mapping process:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{mapping_process_id}", response_model=MappingResponse)
async def get_mapping(process_id: int):
    mapping_pr_id = ObjectId(id)
    mapping_process_docu = await mapping_process_collection.find_one({'_id': mapping_pr_id})
    mappingProcess = get_mapping_process(process_id)
    # TERMINAR ##
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

@router.get("/graph/{process_id}", response_model = Any)
async def get_graph(process_id: str):
    try:
        pid = ObjectId(process_id)
        mapping_process_docu = await mapping_process_collection.find_one({'_id': pid})
        onto_for_graph = await get_ontology_info_from_pid(mapping_process_docu['ontologyId'])
        graph_with_mappings = graph_generator(onto_for_graph, mapping_process_docu['mapping'])
        
    except Exception as e:
        return HTTPException(status_code=500, detail="Internal error while generating the graph ")
    
    return graph_with_mappings

@router.get("/" )
async def get_mappings():
    try :
        mapping_docus =  mapping_process_collection.find({})
        mapping_process_docs = await mapping_docus.to_list(length=None)  
        mappingpr_names = []
        for mapping_process_doc in mapping_process_docs:
            mappingpr = {
                "id": str(mapping_process_doc['_id']),
                "name": mapping_process_doc['name'],
            }
            mappingpr_names.append(mappingpr)
        return mappingpr_names
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response

