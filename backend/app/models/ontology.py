
from pydantic import BaseModel,Field,HttpUrl,model_validator
from typing import Dict, Any, List, Optional
from bson import ObjectId

class OntologyDocument(BaseModel):
    id: Optional[str] = None
    type: str = Field(..., pattern='^(FILE|URI)$', description="Type of the document, either 'FILE' or 'URI'")
    file: Optional[str] = Field(None, description="Path to the file")
    uri: Optional[HttpUrl] = Field(None, description="URI of the ontology")

    # @model_validator(mode="before")
    # def convert_uri_to_str(cls, values):
    #     if "uri" in values and isinstance(values["uri"], HttpUrl):
    #         values["uri"] = str(values["uri"])  # Convierte a cadena al serializar
    #     return values