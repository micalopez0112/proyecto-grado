from fastapi import APIRouter, HTTPException, Query, Body, UploadFile, File
import json

from backend.app.rules_validation.models import  MappingRequest, MappingResponse, PutMappingRequest
from backend.app.dq_evaluation.evaluation import StrategyContext
from app.services import mapping_service as service
from typing import List,Optional, Dict, Any
from neo4j import GraphDatabase

from genson import SchemaBuilder
from pydantic import BaseModel
from app.Coleccion_Películas.governance import cleanJsonSchema
import os

zone_path = os.getenv("ZONE_PATH")

URI = "bolt://localhost:7687"
AUTH = ("neo4j","tesis2024")

router = APIRouter()

class JsonRequest(BaseModel):
    jsonInstances: dict

@router.post("/generate-schema/")
async def get_schema_from_path(collectionFilePath: str):
    try:
        realPath = zone_path + collectionFilePath
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


@router.post("/generate-schemaList/")
async def generate_schema(request: JsonRequestList):
    try:
        builder = SchemaBuilder()
        for json_obj in request.jsonInstances:
            builder.add_object(json_obj)
        schema = builder.to_schema()
        return schema
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

        
@router.post("/generate-schemaListFromFiles/")
async def generate_schema(request: List[UploadFile] = File(...)):
    try:
        builder = SchemaBuilder()
        for file in request:
            content = await file.read() 
            json_data = json.loads(content)
            builder.add_object(json_data) 
        schema = builder.to_schema()
        return schema
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ontology_id/{ontology_id}", response_model = MappingResponse)
async def save_and_validate_mapping(ontology_id: str, mapping_proccess_id: Optional[str] = None, 
                       request: MappingRequest = Body(...)):
    try:
        if not isinstance(request.mapping, dict):
            raise HTTPException(status_code=400, detail="Invalid mapping body")
        
        mapping_inserted_id = await service.validate_and_save_mapping_process(request, mapping_proccess_id, ontology_id)

        return MappingResponse(message="Mapped successfully", status="success",mapping_id=mapping_inserted_id) 
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

        return MappingResponse(message="Mapping process updated successfully", status="success",mapping_id = mapping_process_id)
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
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        
        print(f'request_mapping_body: {request_mapping_body}')
        try :
            context = StrategyContext()
            context.select_strategy(quality_rule)
            
            result = await context.evaluate_quality(mapping_process_id, request_mapping_body, driver)
            return result
        except Exception as e:
            msg = str(e)
            response = MappingResponse(message=msg, status="error")
            return response
        
    driver.close()

@router.get("/schemas/{schema_id}")
async def get_mappings_by_schema_id(schema_id: str):
    try:
        result = await service.get_mappings_by_json_schema(schema_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return result