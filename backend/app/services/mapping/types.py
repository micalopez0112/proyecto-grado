from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models.mapping import MappingProcessDocument, EditMappingRequest


class MappingValidationResult(BaseModel):
    """Result of validating a mapping."""
    is_valid: bool
    errors: list[str] = []
    warnings: list[str] = []

class SchemaData(BaseModel):
    """Data for schema creation/retrieval."""
    document_storage_path: str
    json_schema: Dict[str, Any]
    external_schema_id: Optional[str] = None

class MappingCreateData(BaseModel):
    """Data required to create a new mapping."""
    name: str = Field(default=None)
    mapping: Dict[str, Any] = Field(default=None)
    ontology_id: str = Field(default=None) 
    json_schema: Dict[str, Any] = Field(default=None) 
    # ver como se supone que tendría que venir esto!!
    document_storage_path : Optional[str] = Field(default=None)
    json_schema_id: Optional[str] = Field(default=None)
    
class MappingUpdateData(BaseModel):
    """Data that can be updated in a mapping."""
    name: Optional[str] = None
    description: Optional[str] = None
    mapping: Optional[Dict[str, Any]] = None

class MappingBasicInfo(BaseModel):
    """Basic mapping information response."""
    id: str
    name: str
    
def build_mapping_id_name_tupple(mapping_process_doc) -> Dict[str, str]:
    """Build a tuple with mapping ID and name."""
    return {
        "id": str(mapping_process_doc['_id']),
        "name": mapping_process_doc['name'],
    }

def build_update_data_from_mapping_request(edit_mapping_request: EditMappingRequest):
    update_data ={}
    for key, value in edit_mapping_request:
            if value is not None and value != "" and value != {} and value != "string":
                update_data[key] = value
    return update_data
    
def build_mapping_proccess_response(ontology_data, JSON_schema, mapping, mapping_process_docu):
    return {
            'ontology': ontology_data,
            'schema': JSON_schema,
            'mapping': mapping,
            'mapping_name': mapping_process_docu.name
    }