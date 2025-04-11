from dataclasses import dataclass
from typing import List, Optional
from app.models.mapping import MappingProcessDocument

@dataclass
class CreateDQModelParams:
    """Parameters for creating a DQ model."""
    mapping_process_id: str
    dq_model_name: str
    dq_method_id: Optional[str] = None
    dq_aggregated_method_id: Optional[str] = None
    mapped_entries: Optional[List[str]] = None

@dataclass
class EvaluationParams:
    """Parameters for evaluation queries."""
    dq_model_id: str
    mapping_process_id: str
    json_key: str
    limit: int
    offset: int
