from pydantic import BaseModel,Field,HttpUrl
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
    mapping: Dict[str, Any] = Field()
    jsonSchema: JsonSchema = Field(..., description="Esquema JSON")

# Responses
class MappingResponse(BaseModel):
    status : str
    message : str


class OntologyDocument(BaseModel):
    id: Optional[str] = None
    type: str = Field(..., pattern='^(FILE|URI)$', description="Type of the document, either 'FILE' or 'URI'")
    file: Optional[str] = Field(None, description="Path to the file")
    uri: Optional[HttpUrl] = Field(None, description="URI of the ontology")

class MappingProcessDocument(BaseModel):
    id : Optional[str] = None
    mapping :Optional[Dict[str, Any]]= None
    ontologyId: Optional[str]= None
    jsonSchemaId: Optional[str]= None
    

# Helper function to parse ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")
    
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