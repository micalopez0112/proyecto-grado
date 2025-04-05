from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

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
    name: str
    description: Optional[str] = None
    ontology_id: str
    mapping: Dict[str, Any]
    schema_data: SchemaData
    
class MappingUpdateData(BaseModel):
    """Data that can be updated in a mapping."""
    name: Optional[str] = None
    description: Optional[str] = None
    mapping: Optional[Dict[str, Any]] = None
