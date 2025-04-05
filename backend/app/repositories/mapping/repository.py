from typing import List, Optional, Dict, Any
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

from ..base import BaseRepository
from ..exceptions import EntityNotFoundException
from app.models.mapping import MappingProcessDocument
from app.database import mapping_process_collection

class MappingRepository(BaseRepository[MappingProcessDocument]):
    def __init__(self):
        super().__init__(mapping_process_collection)

    async def find_by_id(self, id: str) -> Optional[MappingProcessDocument]:
        """Find a mapping by its ID."""
        try:
            mapping_obj_id = ObjectId(id)
            doc = await self.collection.find_one({'_id': mapping_obj_id})
            return MappingProcessDocument(**doc) if doc else None
        except Exception as e:
            raise EntityNotFoundException(f"Mapping {id} not found: {str(e)}")

    async def create(self, mapping: MappingProcessDocument) -> str:
        """Create a new mapping process."""
        try:
            result = await self.collection.insert_one(mapping.dict(exclude_unset=True))
            return str(result.inserted_id)
        except Exception as e:
            raise EntityNotFoundException(f"Error creating mapping: {str(e)}")

    async def update(self, id: str, data_to_update: dict, mapping_validated: bool = None) -> bool:
        """Update an existing mapping."""
        try:
            if mapping_validated is not None:
                data_to_update['mapping_suscc_validated'] = mapping_validated

            result = await self.collection.update_one(
                {'_id': ObjectId(id)},
                {'$set': data_to_update}
            )
            return result.modified_count > 0
        except Exception as e:
            raise EntityNotFoundException(f"Error updating mapping {id}: {str(e)}")

    async def delete(self, id: str) -> bool:
        """Delete a mapping by its ID."""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            raise EntityNotFoundException(f"Error deleting mapping {id}: {str(e)}")

    async def find_mappings_by_schema(
        self, 
        schema_id: str, 
        validated: bool = None
    ) -> List[MappingProcessDocument]:
        """Find all mappings associated with a specific schema."""
        query = {'jsonSchemaId': schema_id}
        if validated is not None:
            query['mapping_suscc_validated'] = validated
        
        cursor = self.collection.find(query)
        docs = await cursor.to_list(length=None)
        return [MappingProcessDocument(**doc) for doc in docs]

    async def find_by_query(self, query: Dict[str, Any]) -> List[MappingProcessDocument]:
        """Find mappings by custom query."""
        try:
            cursor = self.collection.find(query)
            docs = await cursor.to_list(length=None)
            return [
                MappingProcessDocument(
                    _id=str(doc['_id']),
                    name=doc.get('name', ''),
                    mapping=doc.get('mapping', {}),
                    ontologyId=doc.get('ontologyId'),
                    jsonSchemaId=doc.get('jsonSchemaId')
                ) 
                for doc in docs
            ]
        except Exception as e:
            logger.error(f"Error in find_by_query: {e}")
            return []
