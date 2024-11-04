


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