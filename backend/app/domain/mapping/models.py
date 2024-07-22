from pydantic import BaseModel
from typing import Dict, Any

# temporary memory storage
mappingProcessInMemory = {}

class MappingProcess(BaseModel):
    id : int
    mapping : Dict[str, Any]
    ontology: Any
    jsonSchema: Any
    
    class Config:
        from_attributes = True

class MappingRequest(BaseModel):
    mapping: Dict[str, Any]

class MappingResponse(BaseModel):
    status : str
    message : str
## esto se reemplaza luego con persistencia
def set_mapping_process(key, value):
    global mappingProcessInMemory
    mappingProcessInMemory[key] = value

def get_mapping_process(key):
    global mappingProcessInMemory
    return mappingProcessInMemory.get(key)

def delete_mapping_process(key):
    global mappingProcessInMemory
    if key in mappingProcessInMemory:
        del mappingProcessInMemory[key]