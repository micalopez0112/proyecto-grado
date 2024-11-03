


from ..database import  jsonschemas_collection
from typing import Dict, Any
from bson import ObjectId
from app.domain.mapping.models import  JsonSchema

async def find_all_schemas():
    cursor = jsonschemas_collection.find({})
    schemas_list = await cursor.to_list(length=None)
    
    return schemas_list

async def insert_schema(json_schema: Dict[str, Any]):
    # ver error sumar excpetion
    schema_result = await jsonschemas_collection.insert_one(json_schema)
    
    schema_id = schema_result.inserted_id
    return schema_id

async def find_schema_by_id(schema_id: str):
    schema_id = ObjectId(schema_id)
    schemaDocum = await jsonschemas_collection.find_one({'_id': schema_id})
    
    JSONSchema = JsonSchema(**schemaDocum)
    return JSONSchema