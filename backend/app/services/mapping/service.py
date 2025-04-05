from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import logging

from app.repositories.mapping.repository import MappingRepository
from app.models.mapping import MappingProcessDocument
from app.services import schema_service, ontology_service
from app.rules_validation.mapping_rules import validate_mapping
from .types import MappingCreateData, MappingUpdateData
from .exceptions import MappingValidationError, MappingNotFoundError, InvalidMappingDataError

logger = logging.getLogger(__name__)

class MappingService:
    def __init__(self, mapping_repository: MappingRepository):
        self.repository = mapping_repository

    async def create_mapping(self, data: MappingCreateData) -> str:
        """
        Create a new mapping process.
        
        Args:
            data: The mapping data to create
            
        Returns:
            str: The ID of the created mapping
            
        Raises:
            MappingValidationError: If the mapping fails validation
            InvalidMappingDataError: If the data is invalid
        """
        try:
            # Get or create schema
            schema_id = await schema_service.get_or_create_schema(
                data.schema_data.document_storage_path,
                data.schema_data.json_schema,
                data.schema_data.external_schema_id or ""
            )
            
            # Get ontology
            ontology = await ontology_service.get_ontology_by_id(data.ontology_id)
            if not ontology:
                raise InvalidMappingDataError(f"Ontology {data.ontology_id} not found")

            # Validate mapping
            json_schema = data.schema_data.json_schema
            json_schema['_id'] = schema_id
            
            is_valid = validate_mapping(data.mapping, ontology, json_schema)
            if not is_valid:
                raise MappingValidationError("Mapping validation failed")

            # Create mapping document
            mapping_doc = MappingProcessDocument(
                name=data.name,
                description=data.description,
                jsonSchemaId=str(schema_id),
                ontologyId=data.ontology_id,
                mapping=data.mapping,
                document_storage_path=data.schema_data.document_storage_path,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                mapping_suscc_validated=True
            )

            # Save to repository
            mapping_id = await self.repository.create(mapping_doc)
            logger.info(f"Created new mapping with ID: {mapping_id}")
            return mapping_id

        except Exception as e:
            logger.error(f"Error creating mapping: {str(e)}")
            raise InvalidMappingDataError(f"Could not create mapping: {str(e)}")

    async def update_mapping(
        self, 
        mapping_id: str, 
        data: MappingUpdateData,
        validate: bool = True
    ) -> bool:
        """
        Update an existing mapping.
        
        Args:
            mapping_id: The ID of the mapping to update
            data: The data to update
            validate: Whether to validate the mapping before updating
            
        Returns:
            bool: True if update was successful
            
        Raises:
            MappingNotFoundError: If the mapping is not found
            MappingValidationError: If the mapping fails validation
        """
        try:
            # Check if mapping exists
            existing = await self.repository.find_by_id(mapping_id)
            if not existing:
                raise MappingNotFoundError(f"Mapping {mapping_id} not found")

            # Prepare update data
            update_data = data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()

            # If mapping is being updated, validate it
            if validate and data.mapping:
                # Get necessary data for validation
                ontology = await ontology_service.get_ontology_by_id(existing.ontologyId)
                schema = await schema_service.get_schema_by_id(existing.jsonSchemaId)
                
                if not ontology or not schema:
                    raise InvalidMappingDataError("Could not find ontology or schema for validation")
                
                # Validate new mapping
                is_valid = validate_mapping(data.mapping, ontology, schema)
                if not is_valid:
                    raise MappingValidationError("Updated mapping validation failed")
                
                update_data["mapping_suscc_validated"] = True

            # Update in repository
            success = await self.repository.update(mapping_id, update_data)
            if success:
                logger.info(f"Updated mapping {mapping_id}")
            return success

        except MappingNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating mapping {mapping_id}: {str(e)}")
            raise InvalidMappingDataError(f"Could not update mapping: {str(e)}")

    async def get_mapping(self, mapping_id: str) -> MappingProcessDocument:
        """Get a mapping by its ID."""
        mapping = await self.repository.find_by_id(mapping_id)
        if not mapping:
            raise MappingNotFoundError(f"Mapping {mapping_id} not found")
        return mapping

    async def get_mappings_by_schema(
        self, 
        schema_id: str,
        validated_only: bool = False
    ) -> List[MappingProcessDocument]:
        """Get all mappings for a specific schema."""
        return await self.repository.find_mappings_by_schema(
            schema_id,
            validated=validated_only if validated_only else None
        )

    async def get_mappings(self, validated_mappings: bool = None) -> List[Dict[str, str]]:
        """Get all mappings with optional validation filter."""
        query = {}
        if validated_mappings is not None and validated_mappings is True:
            query = {'mapping_suscc_validated': validated_mappings}
            
        mapping_process_docs_list = await self.repository.find_by_query(query)
        return [
            {
                "id": str(doc.dict().get('_id', '')),
                "name": doc.name or ''
            }
            for doc in mapping_process_docs_list
        ]
    
    async def delete_mapping(self, mapping_id: str) -> bool:
        """Delete a mapping by its ID."""
        try:
            success = await self.repository.delete(mapping_id)
            if not success:
                raise MappingNotFoundError(f"Mapping {mapping_id} not found")
            logger.info(f"Deleted mapping {mapping_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting mapping {mapping_id}: {str(e)}")
            raise