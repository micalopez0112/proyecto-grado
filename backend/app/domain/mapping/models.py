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
    documentStoragePath : str

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
    # { "destinp": { "type": "object", "properties": {}} }
    required: Optional[List[str]] = None
    # property_name = 
    def findPropertyInJsonSchema(self, property_name: str)-> Optional[Dict[str, Any]]:
        properties = property_name.split("_")[0]
        properties_names = properties.split("-")
        current_level = self.properties
        if len(properties_names) == 1:
            if property_name in current_level:
                return current_level[property_name]
            else:
                return None
   
        print("looking for property!")
        current_level = self.properties[properties_names[0]]
        properties_names = properties_names[1:]
        for prop_name in properties_names:
            if 'properties' in current_level and prop_name in current_level['properties']:
                print("### PROPERTY NAME: ##", prop_name)
                current_level = current_level['properties'][prop_name]
                print("## CURRENT PROP: ##", current_level)
            elif 'items' in current_level:
                items = current_level['items']
                print("## ITEMS: ##", items)
                for item in items:
                    print("## ITEM PROPERTIES: ##", item['properties'])
                    if 'properties' in item and prop_name in item['properties']:
                        current_level = item['properties'][prop_name]
                    else:
                        return None
            else:
                return None
        return current_level
    
#Requests bodys
class MappingRequest(BaseModel):
    name: str = Field(default=None)
    mapping: Dict[str, Any] = Field(default=None) 
    jsonSchema: Dict[str, Any] = Field(default=None) 
    # ver como se supone que tendría que venir esto!!
    documentStoragePath : str = Field(default=None)


class EditMappingRequest(BaseModel):
    mapping_name: str = Field()
    mapping: Dict[str, Any] = Field()
# Responses
class MappingResponse(BaseModel):
    status : str
    message : str
    mapping_id : Optional[str] = None


class OntologyDocument(BaseModel):
    id: Optional[str] = None
    type: str = Field(..., pattern='^(FILE|URI)$', description="Type of the document, either 'FILE' or 'URI'")
    file: Optional[str] = Field(None, description="Path to the file")
    uri: Optional[HttpUrl] = Field(None, description="URI of the ontology")

class MappingProcessDocument(BaseModel):
    _id : Optional[str] = None
    name : str = None
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