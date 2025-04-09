from fastapi import Depends
from typing import Annotated

from app.repositories.mapping.repository import MappingRepository
from app.services.mapping.service import MappingService
from app.repositories.ontology.repository import OntologyRepository
from app.services.ontology.service import OntologyService

def get_mapping_repository() -> MappingRepository:
    """Get an instance of the mapping repository."""
    return MappingRepository()

def get_ontology_repository() -> OntologyRepository:
    """Get an instance of the ontology repository."""
    return OntologyRepository()

def get_ontology_service(
    repo: Annotated[OntologyRepository, Depends(get_ontology_repository)]
) -> OntologyService:
    """Get an instance of the ontology service with its repository dependency."""
    return OntologyService(repo)

def get_mapping_service(
    repo: Annotated[MappingRepository, Depends(get_mapping_repository)],
    ontology_service: Annotated[OntologyService, Depends(get_ontology_service)]
) -> MappingService:
    """Get an instance of the mapping service with its repository and ontology service dependencies."""
    return MappingService(repo, ontology_service)