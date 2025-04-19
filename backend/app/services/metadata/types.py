from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from app.models.mapping import MappingProcessDocument
from app.repositories.metadata.types import SaveDQModelDTO

@dataclass
class CreateDQModelRequest:
    """Request parameters for creating a DQ model."""
    mapping_process_id: str
    dq_model_name: str
    dq_method_id: Optional[str] = None
    dq_aggregated_method_id: Optional[str] = None
    mapped_entries: Optional[List[str]] = None

    @staticmethod
    def to_save_dto(request: 'CreateDQModelRequest', mapping_process_doc: MappingProcessDocument, mapped_entries: Dict[str, Any]) -> SaveDQModelDTO:
        """Transform CreateDQModelRequest into SaveDQModelDTO.
        
        Args:
            request: The request object to transform
            mapping_process_doc: The mapping process document
            mapped_entries: Dictionary of mapped entries
            
        Returns:
            SaveDQModelDTO: The transformed DTO for the repository layer
        """
        return SaveDQModelDTO(
            mapping_process_id=request.mapping_process_id,
            dq_model_name=request.dq_model_name,
            dq_method_id=request.dq_method_id,
            mapping_process_docu=mapping_process_doc,
            dq_aggregated_method_id=request.dq_aggregated_method_id,
            mapped_entries=list(mapped_entries.keys())
        )

@dataclass
class GetEvaluationResultsRequest:
    """Request parameters for getting evaluation results."""
    dq_model_id: str
    mapping_process_id: str
    json_key: str
    limit: int
    offset: int
