from pydantic import BaseModel,Field
from typing import Dict, Any, List, Optional
from bson import ObjectId

class MappingProcess(BaseModel):
    id : int
    mapping : Dict[str, Any]
    ontology: Any
    jsonSchema: Any
    documentStoragePath : str

    class Config:
        from_attributes = True

# This represents the mapping entity in the database
class MappingDocument(BaseModel):
    mapping: Dict[str, Any] = Field(..., description="Mapping field with dynamic structure")

#Requests bodys
class MappingRequest(BaseModel):
    name: str = Field(default=None)
    mapping: Dict[str, Any] = Field(default=None) 
    jsonSchema: Dict[str, Any] = Field(default=None) 
    # ver como se supone que tendría que venir esto!!
    documentStoragePath : str = Field(default=None)

class PutMappingRequest(BaseModel):
    mapping_proccess_id: str = Field(default=None)
    name: str = Field(default=None)
    mapping: Dict[str, Any] = Field(default=None) 
    jsonSchema: Dict[str, Any] = Field(default=None)
    ontology_id:str = Field(default=None)
    documentStoragePath : str = Field(default=None)

class EditMappingRequest(BaseModel):
    name: str = Field()
    mapping: Dict[str, Any] = Field()
# Responses
class MappingResponse(BaseModel):
    status : str
    message : str
    mapping_id : Optional[str] = None


class MappingProcessDocument(BaseModel):
    _id : Optional[str] = None
    name : str = None
    mapping :Optional[Dict[str, Any]]= None
    ontologyId: Optional[str]= None
    jsonSchemaId: Optional[str]= None
    document_storage_path : Optional[str]= None
    mapping_suscc_validated : Optional[bool] = None

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

class MappingsByJSONResponse(BaseModel):
    idMapping : Optional[str] = None
    name : str = None
    mapping :Optional[Dict[str, Any]]= None
    jsonSchemaId: Optional[str]= None