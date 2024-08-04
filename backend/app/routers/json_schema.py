
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
from owlready2 import get_ontology
from typing import Dict, Any
router = APIRouter()

# en este momento es casi un dummy pero esto se va a guardar en la db
@router.post("/{process_id}", response_model=Dict[str, Any])
def save_mapping(process_id: int, mapRequestBody: Dict[str, Any]):
   
    print("saving json schema")

    return mapRequestBody