from pydantic import BaseModel,Field
from typing import Dict, Any, Optional, List
from pymongo import MongoClient
from bson import ObjectId

# temporary memory storage
mappingProcessInMemory = {}

class MappingProcess(BaseModel):
    id : int
    mapping : Dict[str, Any]
    ontology: Any
    jsonSchema: Any
    
    class Config:
        from_attributes = True

# This represents the mapping entity in the database
class MappingDocument(BaseModel):
    mapping: Dict[str, Any] = Field(..., description="Mapping field with dynamic structure")

# ver si no lo muevo para otro lado
# This represents the JSON Schema for the mapping entity
class JsonSchema(BaseModel):
    schema: str = Field(alias="$schema")
    type: str
    properties: Dict[str, Any]
    required: Optional[List[str]] = None

#Requests bodys
class MappingRequest(BaseModel):
    mapping: Dict[str, Any]
    jsonSchema: JsonSchema = Field(..., description="Esquema JSON")
# Responses
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