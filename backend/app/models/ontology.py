
from pydantic import BaseModel,Field,HttpUrl
from typing import Dict, Any, List, Optional
from bson import ObjectId

class OntologyDocument(BaseModel):
    id: Optional[str] = None
    type: str = Field(..., pattern='^(FILE|URI)$', description="Type of the document, either 'FILE' or 'URI'")
    file: Optional[str] = Field(None, description="Path to the file")
    uri: Optional[HttpUrl] = Field(None, description="URI of the ontology")