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

@router.post("/generate-schema/")
async def get_schema_from_path(collectionFilePath: str):
    try:
        realPath = DLzone + collectionFilePath
        with open (realPath,"r",encoding='utf-8') as file:
            builder = SchemaBuilder()
            # data = await file.read()
            file_content = json.load(file)
            json_data = JsonRequestList(jsonInstances=file_content)
            for json_obj in json_data.jsonInstances:
                builder.add_object(json_obj)
            schema = builder.to_schema()
            print(f'## RAW SCHEMA ##: {schema}')
            print("###################################")
            ##add method to clean nulls
            modified_schema = cleanJsonSchema(schema)
            print("## Modified schema ##: ", modified_schema)
            return schema
    except OSError as fileError:
        print("Error en la lectura del archivo de la colección", fileError)
        raise HTTPException(status_code=400, detail=str(fileError))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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

# @router.get("/evaluate/{mapping_process_id}" )
# async def evaluate_dq(mapping_process_id: str) : 
#     await evaluate_data_quality("path", mapping_process_id)

# /evaluate/syntactic_accuracy?mapping_process_id=123
@router.post("/evaluate/{quality_rule}")
async def evaluate_quality(quality_rule: str, mapping_process_id: Optional[str] = Query(None, description="ID for mapping"), request_mapping_body: Dict[str, Any]= Body(...)):
    print(f'request_mapping_body: {request_mapping_body}')
    try :
        context = StrategyContext()
        context.select_strategy(quality_rule)
        
        result = await context.evaluate_quality(mapping_process_id, request_mapping_body)
        return result
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

@router.get("/dataquality/results")
async def get_quality_results(mapping_process_id: Optional[str] = Query(None, description="ID for mapping"), 
                              json_key: Optional[str] = Query(None, description="Json key to get quality results"), 
                              limit: Optional[int] = 100, offset: Optional[int] = 0):
    print(f'request_mapping_body: {mapping_process_id}')
    try :
        result = await service.get_evaluation_results_by_json(mapping_process_id, json_key, limit, offset)
        return result
    except Exception as e:
        msg = str(e)
        response = MappingResponse(message=msg, status="error")
        return response
        