from fastapi import APIRouter, HTTPException, Query, Body
from typing import List,Optional, Dict, Any
from pydantic import BaseModel

from app.services import mapping_service as service
from app.models.mapping import  MappingRequest, MappingResponse, PutMappingRequest
from app.dq_evaluation.evaluation import StrategyContext
from app.Coleccion_Películas.governance import cleanJsonSchema
from ..database import DLzone
from genson import SchemaBuilder
import json

URI = "bolt://localhost:7687"
AUTH = ("neo4j","tesis2024")

router = APIRouter()

class JsonRequest(BaseModel):
    jsonInstances: dict
class JsonRequestList(BaseModel):
    jsonInstances: List[dict]  # Cambiado para aceptar una lista de JSON

@router.post("/ontology_id/{ontology_id}", response_model = MappingResponse)
async def save_and_validate_mapping(ontology_id: str, mapping_proccess_id: Optional[str] = None, 
                       request: MappingRequest = Body(...)):
    try:
        if not isinstance(request.mapping, dict):
            raise HTTPException(status_code= 400, detail="Invalid mapping body")
        mapping_inserted = await service.validate_and_save_mapping_process(request, mapping_proccess_id, ontology_id)
        return MappingResponse(message="Mapped successfully", status="success",mapping_id=str(mapping_inserted)) 
    
    except ValueError as e:
        msg = str(e)
        status = "error"
        response = MappingResponse(message=msg, status="error")
        return response
    except Exception as e:
        print("Error saving mapping process:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/")
async def put_mapping(request: PutMappingRequest = Body(...)):
    try:
        print("REQUEST DEL PUT: ", request)
        mapping_id = await service.update_whole_mapping_process(request)
        return MappingResponse(message="Mapping process updated successfully", status="success",mapping_id = str(mapping_id))
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response


@router.get("/{mapping_process_id}")
async def get_mapping(mapping_process_id: str, filter_dp: Optional[bool] = None):
    try:
        complete_mapping = await service.get_mapping_process_by_id(mapping_process_id, filter_dp)
        return complete_mapping
        
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response

@router.get("/" )
async def get_mappings(validated_mappings: Optional[bool] = None) :
    try :
        mapping_process_names = await service.get_mappings(validated_mappings)

        return mapping_process_names
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response


@router.get("/schemas/{schema_id}")
async def get_mappings_by_schema_id(schema_id: str):
    try:
        result = await service.get_mappings_by_json_schema(schema_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return result