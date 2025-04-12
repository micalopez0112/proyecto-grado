from pydantic import BaseModel
from typing import List
from app.models.mapping import MappingProcessDocument

class SaveDQModelDTO(BaseModel):
    """Data transfer object for saving a DQ model."""
    mapping_process_id: str
    dq_model_name: str
    dq_method_id: str
    mapping_process_docu: MappingProcessDocument
    dq_aggregated_method_id: str
    mapped_entries: List[str]
