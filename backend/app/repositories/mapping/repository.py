from typing import Optional, Dict, Any
from bson import ObjectId
from .exceptions import (
    EntityNotFoundException,
    CreateMappingError,
    UpdateMappingError,
    DeleteMappingError,
    QueryError,
)
from app.models.mapping import MappingProcessDocument
from app.database import mapping_process_collection

class MappingRepository():
    def __init__(self):
        self.collection = mapping_process_collection

    async def find_by_id(self, id: str) -> Optional[MappingProcessDocument]:
        """Find a mapping process by its ID."""
        try:
            mapping_obj_id = ObjectId(id)
            doc = await self.collection.find_one({'_id': mapping_obj_id})
            return MappingProcessDocument(**doc) if doc else None
        except Exception as e:
            raise EntityNotFoundException(f"Mapping {id} not found: {str(e)}")

    async def create(self, mapping_process_document: MappingProcessDocument) -> str:
        """Create a new mapping process."""
        try:
            result = await self.collection.insert_one(mapping_process_document.dict(exclude_unset=True))
            return str(result.inserted_id)
        except Exception as e:
            raise CreateMappingError(f"Error creating mapping: {str(e)}")

    async def update(self, id: str, data_to_update: dict, mapping_validated: bool = None) -> Any:
        """Update an existing mapping."""
        try:
            if mapping_validated is not None:
                data_to_update['mapping_suscc_validated'] = mapping_validated

            result = await self.collection.update_one(
                {'_id': ObjectId(id)},
                {'$set': data_to_update}
            )
            return result
        except Exception as e:
            raise UpdateMappingError(f"Error updating mapping {id}: {str(e)}")

    async def delete(self, id: str) -> bool:
        """Delete a mapping by its ID."""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            raise DeleteMappingError(f"Error deleting mapping {id}: {str(e)}")

    async def find_mappings_by_schema(
        self, 
        json_schema_id: str, 
        validated: bool = None
    ):
        try:
            query = {'jsonSchemaId': json_schema_id}
            if validated is not None:
                query['mapping_suscc_validated'] = validated
            
            cursor = self.collection.find(query)
            docs = await cursor.to_list(length=None)
            return docs
        except Exception as e:
            raise QueryError(f"Error finding mappings by schema: {str(e)}")

    async def find_by_query(self, query: Dict[str, Any], projection: Dict[str, Any] = None):
        """Find mappings by custom query."""
        try:
            mapping_docus =  self.collection.find(query, projection)
            mapping_docus_list = await mapping_docus.to_list(length=None)
            return mapping_docus_list
        except Exception as e:
            raise QueryError(f"Error executing query: {str(e)}")