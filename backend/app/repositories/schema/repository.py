from typing import Dict, Any
from bson import ObjectId
from app.database import jsonschemas_collection
from app.models.schema import JsonSchema

class SchemaRepository:
    def __init__(self, collection=jsonschemas_collection):
        self.collection = collection

    async def find_all(self):
        """Find all schemas."""
        cursor = self.collection.find({})
        schemas_list = await cursor.to_list(length=None)
        return schemas_list

    async def insert(self, json_schema: Dict[str, Any], schema_id: str = None):
        """Insert a new schema."""
        if schema_id is not None and schema_id != '':
            json_schema['_id'] = ObjectId(schema_id)
            json_schema['is_external'] = True
        else:
            json_schema['is_external'] = False
        
        schema_result = await self.collection.insert_one(json_schema)
        return str(schema_result.inserted_id)

    async def find_by_id(self, schema_id: str):
        """Find a schema by its ID."""
        schema_id = ObjectId(schema_id)
        schema_doc = await self.collection.find_one({'_id': schema_id})
        if schema_doc is None:
            return None
        
        return JsonSchema(**schema_doc)

    async def find_one_by_query(self, query: Dict[str, Any]):
        """Find one schema by query."""
        schema_doc = await self.collection.find_one(query)
        if schema_doc is None:
            return None
        
        return JsonSchema(**schema_doc)

    async def delete_by_id(self, schema_id: str):
        """Delete a schema by its ID."""
        schema_object_id = ObjectId(schema_id)
        result = await self.collection.delete_one({"_id": schema_object_id})
        return result.deleted_count > 0
