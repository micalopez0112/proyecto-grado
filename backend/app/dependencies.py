from fastapi import Depends
from typing import Annotated

from app.repositories.mapping.repository import MappingRepository
from app.services.mapping.service import MappingService
from app.repositories.ontology.repository import OntologyRepository
from app.services.ontology.service import OntologyService
from app.repositories.schema.repository import SchemaRepository
from app.services.schema.service import SchemaService
from app.repositories.metadata.repository import MetadataRepository
from app.services.metadata.service import MetadataService

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


def get_metadata_repository() -> MetadataRepository:
    """Get an instance of the metadata repository."""
    return MetadataRepository()

def get_metadata_service(
    mapping_repo: Annotated[MappingRepository, Depends(get_mapping_repository)],
    metadata_repo: Annotated[MetadataRepository, Depends(get_metadata_repository)]
) -> MetadataService:
    """Get an instance of the metadata service with its repository dependencies."""
    return MetadataService(mapping_repo, metadata_repo)

def get_schema_repository() -> SchemaRepository:
    """Get an instance of the schema repository."""
    return SchemaRepository()

def get_schema_service(
    repo: Annotated[SchemaRepository, Depends(get_schema_repository)],
    metadata_repo: Annotated[MetadataRepository, Depends(get_metadata_repository)]
) -> SchemaService:
    """Get an instance of the schema service with its repository dependency."""
    return SchemaService(repo,metadata_repo)

def get_mapping_service(
    repo: Annotated[MappingRepository, Depends(get_mapping_repository)],
    ontology_service: Annotated[OntologyService, Depends(get_ontology_service)],
    schema_service: Annotated[SchemaService, Depends(get_schema_service)]
) -> MappingService:
    """Get an instance of the mapping service with its repository and service dependencies."""
    return MappingService(repo, ontology_service, schema_service)