from fastapi import APIRouter
from app.domain.mapping.models import MappingProcess, get_mapping_process, MappingRequest
from app.domain.mapping.service import process_mapping
from typing import Dict, Any

router = APIRouter()

@router.post("/{process_id}", response_model=None)
def save_mapping(process_id: int, mapRequestBody: MappingRequest):
    mappingProcess = get_mapping_process(process_id)
    mappingProcess.mapping = mapRequestBody.mapping
    print("Starting mapping process:", mappingProcess)
    process_mapping(mappingProcess)
    return {"mappinggg": mapRequestBody.dict()}