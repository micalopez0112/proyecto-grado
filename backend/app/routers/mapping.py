from fastapi import APIRouter, HTTPException
from app.domain.mapping.models import MappingProcess, get_mapping_process, MappingRequest, MappingResponse
from app.domain.mapping.service import process_mapping
from typing import Dict, Any

router = APIRouter()

@router.post("/{process_id}", response_model=MappingResponse)
def save_mapping(process_id: int, mapRequestBody: MappingRequest):
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