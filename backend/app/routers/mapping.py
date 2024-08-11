from fastapi import APIRouter, HTTPException
from app.domain.mapping.models import MappingProcess, get_mapping_process, MappingRequest, MappingResponse
from app.domain.mapping.service import process_mapping
from app.domain.mapping.utils import get_ontology_info_from_pid, graph_generator
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

@router.get("/graph/{process_id}", response_model = Any)
def get_graph(process_id: int):
    try:
        onto_for_graph = get_ontology_info_from_pid(process_id)
        graph_with_mappings = graph_generator(onto_for_graph, get_mapping_process(process_id))
        
    except Exception as e:
        return HTTPException(status_code=500, detail="Internal error while generating the graph ")
    
    return graph_with_mappings