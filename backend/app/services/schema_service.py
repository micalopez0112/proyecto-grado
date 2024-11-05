

from typing import Dict, Any
from app.repositories import schema_repo
from app.models.schema import JSONSchemaResponse

async def get_all_schemas():
    schemas = await schema_repo.find_all_schemas()
    result = []
    for schema in schemas:
        # TODO ajustar nombre de la colección
        jsonSchema = JSONSchemaResponse(id=str(schema['_id']), collection_name="some_name", properties=schema['properties'])
        result.append(jsonSchema)
        
    # TODO ajustar tipo de retorno
    return result

async def get_schema_by_id(schema_id: str):
    schema = await schema_repo.find_schema_by_id(schema_id)
    return schema

async def insert_schema(json_schema: dict):
    schema_id = await schema_repo.insert_schema(json_schema)
    return schema_id

async def find_schema_by_collection_name(collection_name : str):
    schema = await schema_repo.find_one_schema_by_query({'collection_name': collection_name})
    return schema

async def get_or_create_schema(json_schema: Dict[str, Any]):
    collection_name=json_schema['collection_name']
    existent_schema = await find_schema_by_collection_name(collection_name)
    if existent_schema is None:
        inserted_id = await insert_schema(json_schema)
        return inserted_id
    
    return existent_schema.id
