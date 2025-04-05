from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Optional
import logging

from app.dependencies import get_mapping_service
from app.services.mapping.service import MappingService
from app.services.mapping.types import MappingCreateData
from app.services.mapping.exceptions import (
    MappingValidationError,
    MappingNotFoundError,
    InvalidMappingDataError
)
from app.models.mapping import MappingRequest, MappingResponse, PutMappingRequest

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/ontology_id/{ontology_id}", response_model=MappingResponse)
async def save_and_validate_mapping(
    ontology_id: str,
    mapping_proccess_id: Optional[str] = None,
    request: MappingRequest = Body(...),
    mapping_service: MappingService = Depends(get_mapping_service)
):
    """Create or update a mapping process."""
    try:
        if not isinstance(request.mapping, dict):
            raise HTTPException(status_code=400, detail="Invalid mapping body")

        # Prepare mapping data
        mapping_data = MappingCreateData(
            name=request.name,
            description=request.description,
            ontology_id=ontology_id,
            mapping=request.mapping,
            schema_data={
                "document_storage_path": request.documentStoragePath,
                "json_schema": request.jsonSchema,
                "external_schema_id": request.jsonSchemaId
            }
        )

        # Create new mapping or update existing one
        if mapping_proccess_id:
            success = await mapping_service.update_mapping(
                mapping_proccess_id,
                {"mapping": request.mapping}
            )
            if not success:
                raise HTTPException(status_code=404, detail="Mapping not found")
            mapping_id = mapping_proccess_id
        else:
            mapping_id = await mapping_service.create_mapping(mapping_data)

        return MappingResponse(
            message="Mapped successfully",
            status="success",
            mapping_id=str(mapping_id)
        )

    except MappingValidationError as e:
        return MappingResponse(message=str(e), status="error")
    except InvalidMappingDataError as e:
        return MappingResponse(message=str(e), status="error")
    except Exception as e:
        logger.error(f"Error saving mapping process: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/")
async def put_mapping(request: PutMappingRequest = Body(...)):
    try:
        print("REQUEST DEL PUT: ", request)
        mapping_id = await service.update_whole_mapping_process(request)
        return MappingResponse(message="Mapping process updated successfully", status="success",mapping_id = str(mapping_id))
    except Exception as e:
        msg = str(e)
        return MappingResponse(message=msg, status="error")


@router.get("/{mapping_process_id}")
async def get_mapping(mapping_process_id: str, filter_dp: Optional[bool] = None):
    try:
        complete_mapping = await service.get_mapping_process_by_id(mapping_process_id, filter_dp)
        return complete_mapping
        
    except Exception as e:
        msg = str(e)
        return MappingResponse(message=msg, status="error")

@router.get("/")
async def get_mappings(
    validated_mappings: Optional[bool] = None,
    mapping_service: MappingService = Depends(get_mapping_service)
):
    try:
        mapping_process_names = await mapping_service.get_mappings(
            validated_mappings=validated_mappings
        )
        return mapping_process_names
    except Exception as e:
        msg = str(e)
        return MappingResponse(message=msg, status="error")


@router.get("/schemas/{schema_id}")
async def get_mappings_by_schema_id(schema_id: str):
    try:
        result = await service.get_mappings_by_json_schema(schema_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result
@router.delete("/{mapping_process_id}")
async def delete_mapping_by_schema_id(mapping_process_id: str):
    print(f'mapping_process_id: {mapping_process_id}')
    try:
        result = await service.delete_mapping_by_id(mapping_process_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
