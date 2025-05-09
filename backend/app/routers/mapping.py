from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Optional
from pydantic import BaseModel

from app.models.mapping import  MappingRequest, MappingResponse, PutMappingRequest
from app.dependencies import get_mapping_service
from app.services.mapping.service import MappingService
from app.services.mapping.types import MappingCreateData

router = APIRouter()

@router.post("/ontology_id/{ontology_id}", response_model = MappingResponse)
async def create_and_validate_mapping(
    ontology_id: str, 
    mapping_proccess_id: Optional[str] = None, 
    request: MappingRequest = Body(...),
    service: MappingService = Depends(get_mapping_service)):
    mapping_inserted = None
    try:
        if not isinstance(request.mapping, dict):
            raise HTTPException(status_code= 400, detail="Invalid mapping body")
        mapping_create_data = MappingCreateData(name=request.name, mapping=request.mapping, ontology_id=ontology_id,
                                                json_schema=request.jsonSchema, json_schema_id=request.jsonSchemaId,
                                                document_storage_path=request.documentStoragePath)
        mapping_inserted, validation_error = await service.create_or_update_mapping_process_with_validation(mapping_create_data, mapping_proccess_id)
        if validation_error is not None:
            return MappingResponse(message=str(validation_error), status="error", mapping_id=mapping_inserted)
        return MappingResponse(message="Mapped successfully", status="success",mapping_id=str(mapping_inserted)) 
    except Exception as e:
        print("Error saving mapping process:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/")
async def put_mapping(
    request: PutMappingRequest = Body(...),
    service: MappingService = Depends(get_mapping_service)):
    try:
        mapping_create_data = MappingCreateData(name=request.name, mapping=request.mapping, ontology_id=request.ontology_id,
                                                json_schema=request.jsonSchema, json_schema_id="",
                                                document_storage_path=request.documentStoragePath)
        mapping_id, schema_id = await service.create_or_update_mapping_process(mapping_create_data, request.mapping_proccess_id)
        return MappingResponse(message="Mapping process updated successfully", status="success",mapping_id = str(mapping_id))
    except Exception as e:
        print("Error updating mapping process:", e)
        return MappingResponse(message=str(e), status="error")

@router.get("/{mapping_process_id}")
async def get_mapping(mapping_process_id: str, filter_dp: Optional[bool] = None, service: MappingService = Depends(get_mapping_service)):
    try:
        complete_mapping = await service.get_mapping_process_by_id(mapping_process_id, filter_dp)
        return complete_mapping
    except Exception as e:
        return MappingResponse(message=str(e), status="error")

@router.get("/" )
async def get_mappings(
    validated_mappings: Optional[bool] = None,
    service: MappingService = Depends(get_mapping_service)
):
    try :
        mapping_process_names = await service.get_mappings(validated_mappings)
        return mapping_process_names
    except Exception as e:
        return MappingResponse(message=str(e), status="error")

@router.get("/schemas/{schema_id}")
async def get_mappings_by_schema_id(
    schema_id: str,
    service: MappingService = Depends(get_mapping_service)):
    try:
        result = await service.get_mappings_by_json_schema(schema_id)
    except Exception as e:
        print("Error getting mappings by schema id:", e)
        raise HTTPException(status_code=500, detail=str(e))
    
    return result

@router.delete("/{mapping_process_id}")
async def delete_mapping_by_schema_id(mapping_process_id: str, service: MappingService = Depends(get_mapping_service)):
    try:
        result = await service.delete_mapping_by_id(mapping_process_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
