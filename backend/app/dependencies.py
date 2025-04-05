from fastapi import Depends
from typing import Annotated

from app.repositories.mapping.repository import MappingRepository
from app.services.mapping.service import MappingService

def get_mapping_repository() -> MappingRepository:
    return MappingRepository()

def get_mapping_service(
    repo: Annotated[MappingRepository, Depends(get_mapping_repository)]
) -> MappingService:
    return MappingService(repo)