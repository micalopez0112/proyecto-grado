from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
from owlready2 import get_ontology
from app.domain.mapping.models import MappingProcess, set_mapping_process

router = APIRouter()

@router.post("/{process_id}")
def upload_ontology(process_id: int, file: UploadFile = File(...)):
    temp_file_path = f"uploaded_{file.filename}"
    print("temp_file_path:", temp_file_path)
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    ontology = get_ontology(temp_file_path).load()
    classes = list(ontology.classes())
    
    # ahora se crea y se guarda desde memoria, evaluar en que momento crear el mappingProcess y estaría guardado en una db
    mappingProcess = MappingProcess(id=process_id, mapping={}, ontology=ontology, jsonSchema={})
    set_mapping_process(process_id, mappingProcess)

    return JSONResponse(content={
        "filename": file.filename,
        "message": "File uploaded and processed successfully",
        "classes": [cls.name for cls in classes]
    })

